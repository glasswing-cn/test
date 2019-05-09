#include <assert.h>
#include <errno.h>
#include <err.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <sysexits.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/fb.h>

#include "_out_struct.c"

struct buf_object {
	uint32_t width;
	uint32_t height;
	uint32_t pitch;
	int fd;
	uint32_t *vaddr;
	uint32_t size;
} buf;

uint32_t fb_width, fb_height;

uint32_t *pixel(uint32_t x, uint32_t y)
{
	return buf.vaddr + x + y*(buf.width+8) ;
}

int gl_init()
{
	const char *dev_path = getenv("FRAMEBUFFER");
	if ( !dev_path ) {
		dev_path = "/dev/fb0";
	}
	buf.fd = open(dev_path, O_RDWR);
	if ( buf.fd<0 ) {
		err(EX_OSFILE, "%s", dev_path);
		return -EX_OSFILE;
	}

	struct fb_fix_screeninfo fb_finfo;
	bzero(&fb_finfo, sizeof(fb_finfo));
	int error = ioctl(buf.fd, FBIOGET_FSCREENINFO, &fb_finfo);
	if ( error ) {
		err(EX_IOERR, "%s", dev_path);
		return -error;
	}
	out_fb_fix_screeninfo(&fb_finfo);

	struct fb_var_screeninfo fb_vinfo;
	bzero(&fb_vinfo, sizeof(fb_vinfo));
	error = ioctl(buf.fd, FBIOGET_VSCREENINFO, &fb_vinfo);
	if ( error ) {
		err(EX_IOERR, "%s", dev_path);
		return -error;
	}
	out_fb_var_screeninfo(&fb_vinfo);

	buf.width = fb_vinfo.xres_virtual;
	buf.height = fb_vinfo.yres_virtual;
	buf.size = 4*buf.width*buf.height;
	buf.size = 2000*3008*4;
	buf.vaddr = mmap(NULL, buf.size, PROT_READ|PROT_WRITE, MAP_SHARED, buf.fd, 0);
	if ( buf.vaddr == MAP_FAILED ) {
		err(EX_IOERR, "%s", dev_path);
		return -EX_IOERR;
	}
	fb_width = buf.width;
	fb_height = buf.height;
	return 0;
}

int gl_fin()
{
	munmap(buf.vaddr, buf.size);
	return close(buf.fd);
}

void gl_show()
{
}

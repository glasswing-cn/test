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

int dev_fd = 0;
uint32_t *fb_buf = 0;
struct fb_var_screeninfo fb_vinfo;

uint32_t RGBA(uint8_t r, uint8_t g, uint8_t b, uint8_t a)
{
	return (a)<<24 | (r)<<16 | (g)<<8 | (b);
}

#define Xres_workaround		3008
#define pixel(x, y)		(*(fb_buf + x + y*Xres_workaround))
uint32_t get_pixel(int x, int y)
{
	if ( x>=0 && x<fb_vinfo.xres_virtual && y>=0 && y<fb_vinfo.yres_virtual ) {
		return pixel(x, y);
	} else {
		return 0;
	}
}

void set_pixel(int x, int y, uint32_t color)
{
	if ( x>=0 && x<fb_vinfo.xres_virtual && y>=0 && y<fb_vinfo.yres_virtual ) {
		pixel(x, y) = color;
	}
}

void rect(int x, int y, int w, int h, uint32_t color)
{
	for ( int i=x; i<x+w; i++ ) {
		for ( int j=y; j<y+h; j++ ) {
			set_pixel(i, j, color);
		}
	}
}

int fb_init()
{
	const char *dev_path = getenv("FRAMEBUFFER");
	if ( !dev_path ) {
		dev_path = "/dev/fb0";
	}
	dev_fd = open(dev_path, O_RDWR);
	if ( dev_fd<0 ) {
		err(EX_OSFILE, "%s", dev_path);
	}

	int error = ioctl(dev_fd, FBIOGET_VSCREENINFO, &fb_vinfo);
	if ( error ) {
		err(EX_IOERR, "%s", dev_path);
	}
	size_t size = 4 * fb_vinfo.xres_virtual * fb_vinfo.yres_virtual;
	size = 2000*3008*4;
	fb_buf = mmap(NULL, size, PROT_READ|PROT_WRITE, MAP_SHARED, dev_fd, 0);
	if ( fb_buf == MAP_FAILED ) {
		err(EX_IOERR, "%s", dev_path);
	}
	return 0;
}

int fb_finish()
{
	size_t size = 4 * fb_vinfo.xres_virtual * fb_vinfo.yres_virtual;
	size = 2000*3008*4;
	munmap(fb_buf, size);
	return close(dev_fd);
}

int main()
{
	fb_init();

/*	for ( int y=0; y<1000; y+=100 ) {
		for ( int x=0; x<3000; x+=100) {
			rect(x, y, 20, 20, RGBA(0xCC, 0, 0, 0));
			rect(x+80, y, 20, 20, RGBA(0, 0xCC, 0, 0));
		}
	}*/
	uint32_t color = RGBA(0, 0xCC, 0xCC, 0);
	set_pixel(0, 0, color);
	set_pixel(1500, 0, color);
	set_pixel(2999, 0, color);
	set_pixel(0, 1000, color);
	set_pixel(1500, 1000, color);
	set_pixel(2999, 1000, color);
	set_pixel(0, 1999, color);
	set_pixel(1500, 1999, color);
	set_pixel(2999, 1999, color);

	fb_finish();
}

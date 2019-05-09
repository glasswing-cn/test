#include <assert.h>
#include <errno.h>
#include <err.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

#include "_out_struct.c"

struct  drm_object {
	int fd;
	drmModeRes *res;
	drmModeConnector *conn;
} drm_obj;

struct buf_object {
	uint32_t width;
	uint32_t height;
	uint32_t pitch;
	uint32_t fb_id;
	uint32_t handle;
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
	if ( !drmAvailable() ) {
		err(1, "DRM not available");
		return -1;
	}
	int fd = open("/dev/dri/card0", O_RDWR|O_CLOEXEC);
	if ( fd < 0 ) {
		err(1, "Open /dev/dri/card0 file fail");
		return -1;
	}
	drmModeRes *res = drmModeGetResources(fd);
	drmModeConnector *conn = drmModeGetConnector(fd, res->connectors[0]);
	out_drmModeRes(res);
	out_drmModeConnector(conn);

	uint32_t width = conn->modes[0].hdisplay;
	uint32_t height = conn->modes[0].vdisplay;
	struct drm_mode_create_dumb cr;
	cr.width = width;
	cr.height = height;
	cr.bpp = 32;
	drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &cr);

	uint32_t fb_id;
	drmModeAddFB(fd, width, height, 24, 32, cr.pitch, cr.handle, &fb_id);

	struct drm_mode_map_dumb ma;
	ma.handle = cr.handle;
	drmIoctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &ma);

	buf.vaddr = mmap(NULL, cr.size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, ma.offset);
	buf.size = cr.size;
	buf.fb_id = fb_id;
	buf.handle = cr.handle;
	buf.width = width;
	buf.height = height;
	buf.pitch = cr.pitch;

	drm_obj.fd = fd;
	drm_obj.res = res;
	drm_obj.conn = conn;

	fb_width = buf.width;
	fb_height = buf.height;
	return 0;
}

int gl_fin()
{
	drmModeRmFB(drm_obj.fd, buf.fb_id);
	munmap(buf.vaddr, buf.size);
	struct drm_mode_destroy_dumb de;
	de.handle = buf.handle;
	drmIoctl(drm_obj.fd, DRM_IOCTL_MODE_DESTROY_DUMB, &de);

	drmModeFreeConnector(drm_obj.conn);
	drmModeFreeResources(drm_obj.res);
	close(drm_obj.fd);
	return 0;
}

void gl_show()
{
	uint32_t crtc_id = drm_obj.res->crtcs[0];
	uint32_t conn_id = drm_obj.res->connectors[0];
	drmModeSetCrtc(drm_obj.fd, crtc_id, buf.fb_id, 0, 0, &conn_id, 1, drm_obj.conn->modes);
}

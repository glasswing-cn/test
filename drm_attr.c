#include <assert.h>
#include <errno.h>
#include <err.h>
#include <stdint.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

#include "out_struct.c"

int main()
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

	drmVersion *ver = drmGetVersion(fd);
	drmModeRes *res = drmModeGetResources(fd);
	out_drmModeRes(res);
	for ( int i=0; i<(res->count_fbs); i++ ) {
		drmModeFB *fb = drmModeGetFB(fd, res->fbs[i]);
		out_drmModeFB(fb);
		drmModeFreeFB(fb);
	}
	for ( int i=0; i<(res->count_crtcs); i++ ) {
		drmModeCrtc *crtc = drmModeGetCrtc(fd, res->crtcs[i]);
		out_drmModeCrtc(crtc);
		drmModeFreeCrtc(crtc);
	}
	for ( int i=0; i<(res->count_connectors); i++ ) {
		drmModeConnector *conn = drmModeGetConnector(fd, res->connectors[i]);
		out_drmModeConnector(conn);
		drmModeFreeConnector(conn);
	}
	for ( int i=0; i<(res->count_encoders); i++ ) {
		drmModeEncoder *encoder = drmModeGetEncoder(fd, res->encoders[i]);
		out_drmModeEncoder(encoder);
		drmModeFreeEncoder(encoder);
	}

/*
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

	drmModeRmFB(drm_obj.fd, buf.fb_id);
	munmap(buf.vaddr, buf.size);
	struct drm_mode_destroy_dumb de;
	de.handle = buf.handle;
	drmIoctl(drm_obj.fd, DRM_IOCTL_MODE_DESTROY_DUMB, &de);
*/

	drmModeFreeResources(res);
	drmFreeVersion(ver);
	close(fd);
}

void gl_show()
{
/*	uint32_t crtc_id = drm_obj.res->crtcs[0];
	uint32_t conn_id = drm_obj.res->connectors[0];
	drmModeSetCrtc(drm_obj.fd, crtc_id, buf.fb_id, 0, 0, &conn_id, 1, drm_obj.conn->modes);
*/}

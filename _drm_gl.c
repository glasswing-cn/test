#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

#include "_out_struct.c"

uint32_t *fb_vaddr;
uint32_t fb_width, fb_height;

uint32_t *pixel(uint32_t x, uint32_t y)
{
	return fb_vaddr + x + y*(fb_width+8) ;
}

static struct modeset_dev {
	struct modeset_dev *next;

	int fd;
	uint32_t fb_id;
	uint32_t crtc_id;
	uint32_t encoder_id;
	uint32_t connector_id;
	drmModeModeInfo mode;

	uint32_t width;
	uint32_t height;
	uint32_t stride;
	uint32_t handle;
	uint32_t *vaddr;
	uint32_t size;
	drmModeCrtc *saved_crtc;
} *dev_list;

static int modeset_open(const char *path)
{
	if ( !drmAvailable() ) {
		fprintf(stderr, "drm not available\n");
		return -1;
	}
	int fd, ret;
	fd = open(path, O_RDWR|O_CLOEXEC);
	if ( fd < 0 ) {
		ret = -errno;
		fprintf(stderr, "cannot open '%s': %m\n", path);
		return ret;
	}
	uint64_t has_dumb;
	if ( drmGetCap(fd, DRM_CAP_DUMB_BUFFER, &has_dumb) < 0 || !has_dumb ) {
		fprintf(stderr, "drm device '%s' does not support dumb buffers\n", path);
		close(fd);
		return -EOPNOTSUPP;
	}
	return fd;
}

static int modeset_dev_append(struct modeset_dev *head, int fd, uint32_t crtc_id, uint32_t encoder_id, drmModeConnector *conn)
{
	while ( head->next ) {
		struct modeset_dev *curr = head->next;
		if ( curr->crtc_id == crtc_id ) return 0;  // crtc been used
		head = curr;
	}

	struct modeset_dev *dev = malloc( sizeof(*dev) );
	bzero(dev, sizeof(*dev));
	dev->fd = fd;
	dev->crtc_id = crtc_id;
	dev->encoder_id = encoder_id;
	dev->connector_id = conn->connector_id;
	memcpy(&dev->mode, &conn->modes[0], sizeof(dev->mode));
	head->next = dev;
	fprintf(stderr, "add modeset dev : (crtc_id = %d, encoder_id = %d, connector_id = %d)\n", dev->crtc_id, dev->encoder_id, dev->connector_id);
	out_drmModeModeInfo(&dev->mode);
	return 1;
}

static void modeset_dev_list()
{
	struct modeset_dev *dev = dev_list;
	while ( dev ) {
		fprintf(stderr, "dev_list : (crtc_id = %d, encoder_id = %d, connector_id = %d)\n", dev->crtc_id, dev->encoder_id, dev->connector_id);
		dev = dev->next;
	}
}

static void modeset_prepare(int fd)
{
	struct modeset_dev *head = malloc( sizeof(*head) );
	head->next = dev_list;

	drmModeRes *res = drmModeGetResources(fd);
	if ( !res ) {
		fprintf(stderr, "cannot retrieve DRM resources (%d): %m\n", errno);
		return;
	}
	for ( int i=0; i < (res->count_connectors); i++ ) {
		drmModeConnector *conn = drmModeGetConnector(fd, res->connectors[i]);
		if ( !conn || conn->connection!=DRM_MODE_CONNECTED || conn->count_modes==0 ) {
			// skip invalid connector
			if ( conn )
				drmModeFreeConnector(conn);
			continue;
		}
		if ( conn->encoder_id ) {
			// avoid full modeset
			drmModeEncoder *enc = drmModeGetEncoder(fd, conn->encoder_id);
			if ( enc && enc->crtc_id && modeset_dev_append(head, fd, enc->crtc_id, enc->encoder_id, conn) ) {
				drmModeFreeEncoder(enc);
				drmModeFreeConnector(conn);
				continue;
			}
			else if ( enc ) {
				drmModeFreeEncoder(enc);
			}
		}
		for ( int j=0; j< (conn->count_encoders); j++ ) {
			// have to iterate conn->encoders now
			drmModeEncoder *enc = drmModeGetEncoder(fd, conn->encoders[j]);
			if ( !enc ) continue;
			int k;
			for ( k=0; k< (res->count_crtcs); k++ ) {
				if ( (enc->possible_crtcs & (1<<k)) && modeset_dev_append(head, fd, res->crtcs[k], enc->encoder_id, conn) )
					break;
			}
			drmModeFreeEncoder(enc);
			if ( k< (res->count_crtcs) ) {  // conn find crtc
				drmModeFreeConnector(conn);
				break;
			}
		}
		drmModeFreeConnector(conn);
	}
	drmModeFreeResources(res);

	dev_list = head->next;
	free(head);
}

static int modeset_create_fb(struct modeset_dev *dev)
{
	int ret;
	struct drm_mode_create_dumb creq;
	struct drm_mode_destroy_dumb dreq;
	struct drm_mode_map_dumb mreq;

	// create dumb buffer
	bzero(&creq, sizeof(creq));
	creq.width = dev->mode.hdisplay;
	creq.height = dev->mode.vdisplay;
	creq.bpp = 32;
	ret = drmIoctl(dev->fd, DRM_IOCTL_MODE_CREATE_DUMB, &creq);
	if ( ret<0 ) {
		fprintf(stderr, "cannot create dumb buffer (%d): %m\n", errno);
		return -errno;
	}
	dev->width = creq.width;
	dev->height = creq.height;
	dev->stride = creq.pitch;
	dev->size = creq.size;
	dev->handle = creq.handle;

	// create framebuffer
	ret = drmModeAddFB(dev->fd, dev->width, dev->height, 24, 32, dev->stride, dev->handle, &dev->fb_id);
	if ( ret ) {
		fprintf(stderr, "cannot create framebuffer (%d): %m\n", errno);
		ret = - errno;
		goto err_destroy;
	}

	// prepare buffer for memory mapping
	bzero(&mreq, sizeof(mreq));
	mreq.handle = dev->handle;
	ret = drmIoctl(dev->fd, DRM_IOCTL_MODE_MAP_DUMB, &mreq);
	if ( ret ) {
		fprintf(stderr, "cannot map dumb buffer (%d): %m\n", errno);
		ret = -errno;
		goto err_fb;
	}

	// actual memory mapping
	dev->vaddr = mmap(0, dev->size, PROT_READ|PROT_WRITE, MAP_SHARED, dev->fd, mreq.offset);
	if ( dev->vaddr == MAP_FAILED ) {
		fprintf(stderr, "cannot mmap dumb buffer (%d): %m\n", errno);
		ret = -errno;
		goto err_fb;
	}

	return 0;
err_fb:
	drmModeRmFB(dev->fd, dev->fb_id);
err_destroy:
	bzero(&dreq, sizeof(dreq));
	dreq.handle = dev->handle;
	drmIoctl(dev->fd, DRM_IOCTL_MODE_DESTROY_DUMB, &dreq);
	return ret;
}

static void modeset_clean_fb(struct modeset_dev *dev)
{
	if ( !dev->fb_id ) return;

	if ( dev->saved_crtc ) {
		drmModeCrtc *sv = dev->saved_crtc;
		drmModeSetCrtc(dev->fd, sv->crtc_id, sv->buffer_id, sv->x, sv->y, &dev->connector_id, 1, &sv->mode);
		drmModeFreeCrtc(sv);
		dev->saved_crtc = 0;
	}

	munmap(dev->vaddr, dev->size);
	drmModeRmFB(dev->fd, dev->fb_id);
	struct drm_mode_destroy_dumb dreq;
	bzero(&dreq, sizeof(dreq));
	dreq.handle = dev->handle;
	drmIoctl(dev->fd, DRM_IOCTL_MODE_DESTROY_DUMB, &dreq);
}

static void modeset_show_fb(struct modeset_dev *dev)
{
	if ( !dev->fb_id ) return;
	if ( !dev->saved_crtc )
		dev->saved_crtc = drmModeGetCrtc(dev->fd, dev->crtc_id);
	drmModeSetCrtc(dev->fd, dev->crtc_id, dev->fb_id, 0, 0, &dev->connector_id, 1, &dev->mode);
}

int gl_init()
{
	int fd = modeset_open("/dev/dri/card0");
	if ( fd<0 ) {
		return fd;
	}
	modeset_prepare(fd);
	modeset_dev_list();
	if ( !dev_list ) {
		close(fd);
		return -1;
	}
	modeset_create_fb(dev_list);

	fb_width = dev_list->width;
	fb_height = dev_list->height;
	fb_vaddr = dev_list->vaddr;
	return 0;
}

int gl_fin()
{
	struct modeset_dev *dev = dev_list;
	while ( dev ) {
		modeset_clean_fb(dev);
		dev = dev->next;
	}
	close(dev_list->fd); // ??
	return 0;
}

void gl_show()
{
	struct modeset_dev *dev = dev_list;
	while ( dev ) {
		modeset_show_fb(dev);
		dev = dev->next;
	}
}

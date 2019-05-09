/* test_gl.c
 * 
 * a tiny graphics library for testing of framebuffer based graph.
 */

#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>

// extern impliment
typedef uint32_t color_t;
color_t XRGB(uint8_t x, uint8_t r, uint8_t g, uint8_t b)
{
	return (x<<24) | (r<<16) | (g<<8) | (b) ;
}
extern const uint32_t fb_width, fb_height;
extern color_t *pixel(uint32_t x, uint32_t y);

extern int gl_init();
extern int gl_fin();
extern void gl_show();

// tiny gl drawing function
color_t get_pixel(uint32_t x, uint32_t y)
{
	if ( x<fb_width && y<fb_height ) {
		return *pixel(x, y);
	} else {
		return 0;
	}
}

void set_pixel(uint32_t x, uint32_t y, color_t color)
{
	if ( x<fb_width && y<fb_height ) {
		*pixel(x, y) = color;
	}
}

void rect(uint32_t x, uint32_t y, uint32_t w, uint32_t h, color_t color)
{
	for ( int i=0; i<w; i++ )
	for ( int j=0; j<h; j++ )
		set_pixel(x+i, y+j, color);
}

// main ...
int main()
{
	int ret = gl_init();
	if ( ret<0 ) {
		fprintf(stderr, "tiny gl initial failure (%d). %m\n", ret);
		return ret;
	}

	color_t color = XRGB(0, 0, 0xCC, 0xCC);
	set_pixel(0, 0, color);
	set_pixel(1500, 0, color);
	set_pixel(2999, 0, color);
	set_pixel(0, 1000, color);
	set_pixel(1500, 1000, color);
	set_pixel(2999, 1000, color);
	set_pixel(0, 1999, color);
	set_pixel(1500, 1999, color);
	set_pixel(2999, 1999, color);
	color = XRGB(0, 0x70, 0xF0, 0x60);
	rect(1480, 900, 40, 90, color);
	gl_show();
	getchar();

	gl_fin();
}

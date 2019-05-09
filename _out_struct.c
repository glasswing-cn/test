///////////////////////////////////////////////

#define __PRELUDE   "\t\t\t\t\t\t\t\t\t\t\t\t"
int __level = 0;


#define _OUT_STRUCT(x)	\
void out_##x ( x *s ) \
{ \
	printf("%.*s", __level, __PRELUDE); \
	printf("%s {\n", #x);


#define _FIN_STRUCT \
	printf("%.*s", __level, __PRELUDE); \
	printf("}\n"); \
}


#define _OUT_STRUCT_STT(x)	\
void out_##x ( struct x *s ) \
{ \
	printf("%.*s", __level, __PRELUDE); \
	printf("struct %s {\n", #x);


#define _PRT_STT_S(x) \
	printf("%.*s", __level, __PRELUDE); \
	printf("\t.%s = \"%s\"\n", #x, s-> x);

#define _PRT_STT_1(x) \
	printf("%.*s", __level, __PRELUDE); \
	printf("\t.%s = %ld\n", #x, s-> x);

#define _PRT_STT_2(x, y) \
	printf("%.*s", __level, __PRELUDE); \
	printf("\t.%s, .%s = %ld, %ld\n", #x, #y, s-> x, s-> y);

#define _PRT_STT_3(x, y, z) \
	printf("%.*s", __level, __PRELUDE); \
	printf("\t.%s, .%s, .%s = %ld, %ld, %ld\n", #x, #y, #z, s-> x, s-> y, s-> z);

#define _PRT_STT_4(x, y, z, t) \
	printf("%.*s", __level, __PRELUDE); \
	printf("\t.%s, .%s, .%s, .%s = %ld, %ld, %ld, %ld\n", #x, #y, #z, #t, s-> x, s-> y, s-> z, s-> t);

#define _PRT_STT_L(x, n) \
	printf("%.*s", __level, __PRELUDE); \
	printf("\t.%s[] = ", #x); \
	for ( int i=0; i<(n); i++ ) printf("%ld, ", (s-> x)[i]); \
	printf("\n");


#define _PRT_STT_STT(t, x) \
	printf("%.*s", __level, __PRELUDE); \
	printf("\t.%s = \n", #x); \
	__level++; \
	out_##t ( &(s-> x) ); \
	__level--;

#define _PRT_STT_STT_L(t, x, n) \
	printf("%.*s", __level, __PRELUDE); \
	printf("\t.%s[] = \n", #x); \
	__level++; \
	for ( int i=0; i<(n); i++ ) out_##t ( (s-> x)+i ); \
	__level--;


////////////////////////////////////////////////
#ifdef _XF86DRM_H_

_OUT_STRUCT( drmModeRes )

	_PRT_STT_L(fbs, s->count_fbs)
	_PRT_STT_L(crtcs, s->count_crtcs)
	_PRT_STT_L(connectors, s->count_connectors)
	_PRT_STT_L(encoders, s->count_encoders)

	_PRT_STT_2(min_width, max_width)
	_PRT_STT_2(min_height, max_height)

_FIN_STRUCT


_OUT_STRUCT( drmModeModeInfo )

	_PRT_STT_1(clock)
	_PRT_STT_3(hdisplay, hsync_start, hsync_end)
	_PRT_STT_2(htotal, hskew)
	_PRT_STT_3(vdisplay, vsync_start, vsync_end)
	_PRT_STT_2(vtotal, vscan)
	_PRT_STT_1(vrefresh)
	_PRT_STT_1(flags)
	_PRT_STT_1(type)

	_PRT_STT_S(name)

_FIN_STRUCT


_OUT_STRUCT( drmModeFB )

	_PRT_STT_1(fb_id)
	_PRT_STT_2(width, height)
	_PRT_STT_1(pitch)
	_PRT_STT_1(bpp)
	_PRT_STT_1(depth)
	_PRT_STT_1(handle)

_FIN_STRUCT


_OUT_STRUCT( drmModeCrtc )

	_PRT_STT_1(crtc_id)
	_PRT_STT_1(buffer_id)
	_PRT_STT_2(x, y)
	_PRT_STT_2(width, height)
	_PRT_STT_1(mode_valid)
	_PRT_STT_STT(drmModeModeInfo, mode)

	_PRT_STT_1(gamma_size)

_FIN_STRUCT


_OUT_STRUCT( drmModeEncoder )

	_PRT_STT_1(encoder_id)
	_PRT_STT_1(encoder_type)
	_PRT_STT_1(crtc_id)
	_PRT_STT_1(possible_crtcs)
	_PRT_STT_1(possible_clones)

_FIN_STRUCT


_OUT_STRUCT( drmModeConnector )

	_PRT_STT_1(connector_id)
	_PRT_STT_1(encoder_id)
	_PRT_STT_1(connector_type)
	_PRT_STT_1(connector_type_id)
	_PRT_STT_1(connection)
	_PRT_STT_2(mmWidth, mmHeight)
	_PRT_STT_1(subpixel)

	_PRT_STT_STT_L(drmModeModeInfo, modes, s->count_modes)

	_PRT_STT_L(props, s->count_props)
	_PRT_STT_L(prop_values, s->count_props)

	_PRT_STT_L(encoders, s->count_encoders)

_FIN_STRUCT


_OUT_STRUCT( drmModePlane )

	_PRT_STT_L(formats, s->count_formats)
	_PRT_STT_1(plane_id)

	_PRT_STT_1(crtc_id)
	_PRT_STT_1(fb_id)
	_PRT_STT_2(crtc_x, crtc_y)
	_PRT_STT_2(x, y)

	_PRT_STT_1(possible_crtcs)
	_PRT_STT_1(gamma_size)

_FIN_STRUCT


_OUT_STRUCT( drmModePlaneRes )

	_PRT_STT_L(planes, s->count_planes)

_FIN_STRUCT


////////////////////////////////////////////////////////////////////

_OUT_STRUCT( drmVersion )

	_PRT_STT_1(version_major)
	_PRT_STT_1(version_minor)
	_PRT_STT_1(version_patchlevel)
	_PRT_STT_S(name)
	_PRT_STT_S(date)
	_PRT_STT_S(desc)

_FIN_STRUCT

#endif

////////////////////////////////////////////////////////////////////

#ifdef _LINUX_FB_H

_OUT_STRUCT_STT( fb_fix_screeninfo )

	_PRT_STT_S(id)
	_PRT_STT_1(smem_start)
	_PRT_STT_1(smem_len)
	_PRT_STT_1(type)
	_PRT_STT_1(type_aux)
	_PRT_STT_1(visual)
	_PRT_STT_3(xpanstep, ypanstep, ywrapstep)
	_PRT_STT_1(line_length)
	_PRT_STT_1(mmio_start)
	_PRT_STT_1(mmio_len)
	_PRT_STT_1(accel)
	_PRT_STT_1(capabilities)
	_PRT_STT_2(reserved[0], reserved[1])

_FIN_STRUCT


_OUT_STRUCT_STT( fb_var_screeninfo )

	_PRT_STT_2(xres, yres)
	_PRT_STT_2(xres_virtual, yres_virtual)
	_PRT_STT_2(xoffset, yoffset)

	_PRT_STT_1(bits_per_pixel)
	_PRT_STT_1(grayscale)

	_PRT_STT_3(red.offset, red.length, red.msb_right)
	_PRT_STT_3(green.offset, green.length, green.msb_right)
	_PRT_STT_3(blue.offset, blue.length, blue.msb_right)
	_PRT_STT_3(transp.offset, transp.length, transp.msb_right)

	_PRT_STT_1(nonstd)
	_PRT_STT_1(activate)
	_PRT_STT_2(height, width)
	_PRT_STT_1(accel_flags)

	_PRT_STT_4(left_margin, right_margin, upper_margin, lower_margin)
	_PRT_STT_2(hsync_len, vsync_len)
	_PRT_STT_1(sync)
	_PRT_STT_1(vmode)
	_PRT_STT_1(rotate)
	_PRT_STT_1(colorspace)
	_PRT_STT_4(reserved[0], reserved[1], reserved[2], reserved[3])

_FIN_STRUCT

#endif

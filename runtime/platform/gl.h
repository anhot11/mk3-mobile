/*
 * The one place that knows where the GL headers live.
 *
 * Win32 needs windows.h pulled in first or GL/gl.h will not compile; Apple
 * moved the headers into a framework. Nothing else in the tree should include
 * a GL header directly.
 */
#ifndef LIME_GL_H
#define LIME_GL_H

#if defined(_WIN32) && !defined(_WIN64)
/* 32-bit Windows: opengl32.dll exports __stdcall entry points, but the
 * decompiled files declare the GL calls they make themselves, as plain C
 * functions -- `void glDisable(unsigned cap);` -- the way the ARM binary
 * called them. On x86-64 and ARM there is one calling convention and the
 * two agree; here they do not, and the mismatch is a compile error at best
 * and a corrupted stack at worst. So on this target every GL declaration is
 * plain cdecl, and runtime/platform/win32_gl_cdecl.c forwards each one to
 * the real entry point. */
#  include <windows.h>
#  pragma push_macro("APIENTRY")
#  pragma push_macro("WINGDIAPI")
#  undef  APIENTRY
#  undef  WINGDIAPI
#  define APIENTRY
#  define WINGDIAPI
#  include <GL/gl.h>
#  pragma pop_macro("WINGDIAPI")
#  pragma pop_macro("APIENTRY")
#elif defined(_WIN32)
#  include <windows.h>
#  include <GL/gl.h>
#elif defined(__APPLE__)
#  include <OpenGL/gl.h>
#elif defined(__ANDROID__)
#  include <GLES/gl.h>
#  include <GLES/glext.h>

#  define GL_QUADS 0x0007
#  define glOrtho(l, r, b, t, n, f) glOrthof((GLfloat)(l), (GLfloat)(r), (GLfloat)(b), (GLfloat)(t), (GLfloat)(n), (GLfloat)(f))
#  define glClearDepth(d) glClearDepthf((GLclampf)(d))
#  define glFrustum(l, r, b, t, n, f) glFrustumf((GLfloat)(l), (GLfloat)(r), (GLfloat)(b), (GLfloat)(t), (GLfloat)(n), (GLfloat)(f))

typedef struct {
    GLfloat x, y;
    GLfloat u, v;
} gles_compat_vert_t;

static gles_compat_vert_t g_gles_vbuf[8];
static int g_gles_vcount = 0;
static GLfloat g_gles_cur_u = 0.0f, g_gles_cur_v = 0.0f;

static inline void glTexCoord2f(GLfloat u, GLfloat v) {
    g_gles_cur_u = u;
    g_gles_cur_v = v;
}

static inline void glVertex2f(GLfloat x, GLfloat y) {
    if (g_gles_vcount < 8) {
        g_gles_vbuf[g_gles_vcount].x = x;
        g_gles_vbuf[g_gles_vcount].y = y;
        g_gles_vbuf[g_gles_vcount].u = g_gles_cur_u;
        g_gles_vbuf[g_gles_vcount].v = g_gles_cur_v;
        g_gles_vcount++;
    }
}

static inline void glBegin(GLenum mode) {
    (void)mode;
    g_gles_vcount = 0;
}

static inline void glEnd(void) {
    if (g_gles_vcount > 0) {
        GLfloat pos[16], tex[16];
        for (int i = 0; i < g_gles_vcount; i++) {
            pos[i*2] = g_gles_vbuf[i].x;
            pos[i*2+1] = g_gles_vbuf[i].y;
            tex[i*2] = g_gles_vbuf[i].u;
            tex[i*2+1] = g_gles_vbuf[i].v;
        }
        glEnableClientState(GL_VERTEX_ARRAY);
        glEnableClientState(GL_TEXTURE_COORD_ARRAY);
        glVertexPointer(2, GL_FLOAT, 0, pos);
        glTexCoordPointer(2, GL_FLOAT, 0, tex);
        glDrawArrays(GL_TRIANGLE_FAN, 0, g_gles_vcount);
        glDisableClientState(GL_TEXTURE_COORD_ARRAY);
        glDisableClientState(GL_VERTEX_ARRAY);
        g_gles_vcount = 0;
    }
}
#else
#  include <GL/gl.h>
#endif

#endif

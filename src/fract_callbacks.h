#ifndef _FRACT_CALLBACKS_H_
#define _FRACT_CALLBACKS_H_

#ifdef __cplusplus
extern "C" {
#endif

// these are the only gf4d_fractal functions that fract needs to call
// they're broken out here to insulate the fractal-drawing code from
// the front-end

    void gf4d_fractal_parameters_changed(Gf4dFractal *f);
    void gf4d_fractal_image_changed(Gf4dFractal *f, int x1, int x2, int y1, int y2);
    void gf4d_fractal_progress_changed(Gf4dFractal *f, float progress);
    void gf4d_fractal_status_changed(Gf4dFractal *f, int status_val);

#ifdef __cplusplus
}
#endif

#endif /* _FRACT_CALLBACKS_H_ */

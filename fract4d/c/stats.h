
typedef enum
{
    DEEPEN_STATS,
    TOLERANCE_STATS
} stat_type_t;

typedef struct s_pixel_stat pixel_stat_t;

struct s_pixel_stat{

    // total number of iterations performed
    unsigned long iterations;
    
    // pixels we processed
    unsigned long pixels;

    // number of pixels we actually called calc() on
    unsigned long pixels_calculated;

    // number of pixels we guessed (calculated + skipped == pixels)
    unsigned long pixels_skipped;

    // pixels which wound up inside
    unsigned long pixels_inside;

    // pixels which would up outside (inside + outside == pixels)
    unsigned long pixels_outside;

    // n pixels correctly classified that would be wrong 
    // if we calculated half the iterations
    int worse_depth_pixels;

    // n pixels currently misclassified that would be correct 
    // if we doubled the iterations
    int better_depth_pixels; 

    // n pixels correctly classified that would be wrong 
    // if we calculated with looser tolerance
    int worse_tolerance_pixels;

    // n pixels currently misclassified that would be correct 
    // if we tightened the tolerance
    int better_tolerance_pixels; 

    s_pixel_stat() {
	reset();
    };

    void reset() {
	iterations=0;
	pixels=0;

	pixels_calculated = 0;
	pixels_skipped = 0;

	pixels_inside = 0;
	pixels_outside = 0;

	worse_depth_pixels=0;
	better_depth_pixels=0;

	worse_tolerance_pixels = 0;
	better_tolerance_pixels = 0;

    };
    void add(const pixel_stat_t& other) {
	iterations += other.iterations;
	pixels += other.pixels;
	pixels_calculated += other.pixels_calculated;
	pixels_skipped += other.pixels_skipped;
	
	pixels_inside += other.pixels_inside;
	pixels_outside += other.pixels_outside;

	worse_depth_pixels += other.worse_depth_pixels;
	better_depth_pixels += other.better_depth_pixels;

	worse_tolerance_pixels += other.worse_tolerance_pixels;
	better_tolerance_pixels += other.better_tolerance_pixels;

    };

    double worse_depth_ratio() const { return ((double)worse_depth_pixels)/pixels; }
    double better_depth_ratio() const { return ((double)better_depth_pixels)/pixels; }

    double worse_tolerance_ratio() const { return ((double)worse_tolerance_pixels)/pixels; }
    double better_tolerance_ratio() const { return ((double)better_tolerance_pixels)/pixels; }

};


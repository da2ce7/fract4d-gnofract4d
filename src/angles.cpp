#include "angles.h"
#include "callbacks.h"
#include "gf4d_angle.h"

void angle_set_cb(GtkAdjustment *adj, gpointer user_data);
void angle_update_cb(GtkWidget *adj, gpointer user_data);
void adjustment_update_callback(Gf4dFractal *gf, gpointer user_data);

void angle_set_cb (GtkAdjustment *adj, gpointer user_data)
{
    char buf[100];
    set_cb_data *pdata = (set_cb_data *)user_data;
    sprintf(buf,"%g",adj->value);
    if(model_cmd_start(pdata->m))
    {
        gf4d_fractal_set_param(model_get_fract(pdata->m),pdata->pnum, buf);
        model_cmd_finish(pdata->m);
    }
}

void angle_update_cb(GtkWidget *w, gpointer user_data)
{
    char buf[100];
    Gf4dAngle *angle = GF4D_ANGLE(w);
    GtkAdjustment *adj = gf4d_angle_get_adjustment(angle);
    sprintf(buf,"%g",180.0 / M_PI * adj->value);
    gnome_appbar_push(GNOME_APPBAR(user_data), buf);
}

void adjustment_update_callback(Gf4dFractal *gf, gpointer user_data)
{
    set_cb_data *pdata = (set_cb_data *)user_data;
    gchar *sval = gf4d_fractal_get_param(gf,pdata->pnum);
    gfloat fval;
    sscanf(sval,"%f",&fval);
    gtk_adjustment_set_value(pdata->adj, fval);

    g_free(sval);
}

GtkWidget*
create_angle_button(
    char *label_text, param_t data, model_t *m, GtkWidget *appbar)
{
	GtkWidget *angle;
	GtkAdjustment *adjustment;
	set_cb_data *pdata;

	adjustment = GTK_ADJUSTMENT(gtk_adjustment_new(0, 0.0, M_PI * 2.0, 0.01, 0.01, 0));
	angle = gf4d_angle_new(adjustment);
	gf4d_angle_set_update_policy(GF4D_ANGLE(angle),GTK_UPDATE_DISCONTINUOUS);
	gf4d_angle_set_label(GF4D_ANGLE(angle),label_text);

	pdata = g_new0(set_cb_data,1);
	pdata->m = m;
	pdata->pnum = data;
	pdata->adj = adjustment;

	gtk_widget_show(angle);
	
	gtk_signal_connect(GTK_OBJECT(adjustment),"value_changed",
			   (GtkSignalFunc)angle_set_cb, pdata );

	gtk_signal_connect(GTK_OBJECT(angle),"value_slightly_changed",
			   (GtkSignalFunc)angle_update_cb, appbar );
	
	gtk_signal_connect(GTK_OBJECT(model_get_fract(m)),"parameters_changed",
			   (GtkSignalFunc)adjustment_update_callback, pdata);	
	return angle;
}




def _get_figure(self, func):
        if plt:
            matplotlib.use('Agg')
           
        if self._is_figure_changed(func):
            fig_object, func = self._reload_func_source(func)
            if callable(func):
                fig_object = FigureObject()
                try:
                    fig = func(*self.plt_args, **self.plt_kwargs)
                except Exception as e:             # noqa
                    fig_object.error = e
                    if self.silent:
                        return fig_object
                    else:
                        raise e
                else:
                    if not isinstance(fig, plt.Figure):
                        fig_object.error = "%s should return instance of class"\
                                        " Matplotlib.Figure" % self.figure
                        if self.silent:
                            return fig_object
                        else:
                            raise TypeError(fig_object.error)
                # build fig_object from matplotlib figure
                fig_object.width = self.fig_width
                fig_object.height = self.fig_height
                fig_object.type = self.output_type
                fig_object.format = self.output_format
                if self.output_type == 'file':
                    if not MEDIA_ROOT and self.silent:
                        fig_object.error = "MEDIA_ROOT isn't configured. "
                        "Check your project settings file."
                        return fig_object
                    elif not MEDIA_ROOT:
                        raise ImproperlyConfigured("You need to set up MEDIA_ROOT"
                            " variable in your project sttings file.")
                    fig_object.path = self.suggest_filename
                    fig_object.source = ''
                    fig.savefig(fig_object.path, format=self.output_format,
                                bbox_inches='tight')
                    if self.fig_cleanup:
                        atexit.register(cleanup_file, fig_object.path)
                elif self.output_type == 'string':
                    buffer = BytesIO()
                    fig.savefig(buffer, format=self.output_format,
                                bbox_inches='tight')
                    buffer.seek(0)
                    fig_object.path = ''
                    if self.output_format == 'png':
                        fig_object.source = b64en(buffer.read()).decode('utf-8')
                    else:
                        fig_object.source =buffer.read().decode('utf-8')
                    plt.close(fig)
                else:
                    fig_object.error = "Undefined figure type. "
                    "Check out field's 'output_type' argument."
                if fig_object.path or fig_object.source:
                    self._fig_hash = self._get_figure_hash(func)
                self._figure_object = fig_object
        
            else:
                self._figure_object = fig_object
                self._fig_hash = ''
                return fig_object
        return self._figure_object
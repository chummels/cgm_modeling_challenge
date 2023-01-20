import palettable

# Colors to use throughout for revised vs original
modeled_color = palettable.cartocolors.qualitative.Safe_10.mpl_colors[1]
revised_color = palettable.cartocolors.qualitative.Safe_10.mpl_colors[0]
colors_for_variations = {
    'original': modeled_color,
    'high-z': revised_color,
}

property_labels = {
    'vlos': r'$v_{\rm LOS}$ [km/s]',
    'T': r'T [K]',
    'nH': r'$n_{\rm H}$ [cm$^{-3}$]',
    'Z': r'$Z$ [$Z_{\odot}$]',
    'NHI': r'$N_{\rm H\,I}$ [cm$^{-2}$]',
}
property_labels_no_units = {
    'vlos': r'$v_{\rm LOS}$',
    'T': r'T',
    'nH': r'$n_{\rm H}$',
    'Z': r'$Z$',
    'NHI': r'$N_{\rm H\,I}$',
}
property_labels_1D = {
    'vlos': r'$\frac{ d N_{\rm H\,I} }{d v_{\rm LOS}}$',
    'T': r'$\frac{ d N_{\rm H\,I} }{d \log T}$',
    'nH': r'$\frac{ d N_{\rm H\,I} }{d \log n_{\rm H}}$',
    'Z': r'$\frac{ d N_{\rm H\,I} }{d \log Z}$',
    'NHI': r'$\frac{ d N_{\rm H\,I} }{d \log N_{\rm H\,I}}$',
}
correlation_coefficient_property_labels = {}
for key, item in property_labels.items():
    unitless_label = item.split( '[' )[0]
    correlation_coefficient_property_labels[key] = r'$r($ ' + unitless_label + r'$)$'
correlation_coefficient_property_labels['all'] = r'$r($ all $)$'
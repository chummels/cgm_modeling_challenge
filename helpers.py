import matplotlib
import palettable

# Colors to use throughout for revised vs original
blinded_color = palettable.cartocolors.qualitative.Safe_10.mpl_colors[1]
revised_color = palettable.cartocolors.qualitative.Safe_10.mpl_colors[0]
colors_for_variations = {
    'original': blinded_color,
    'high-z': revised_color,
}

# For interpreting units
property_given_key = {
    'nH': 'Density',
    'NHI': 'HI Column',
    'vlos': 'LOS Velocity',
    'l': 'Lengths',
    'Z': 'Metallicity',
    'pdf': 'PDF Value',
    'T': 'Temperature',
    'x': 'LOS Position',
}
key_given_property = {}
for prop_key, prop in property_given_key.items():
    key_given_property[prop] = prop_key
logscale = {
    'vlos': False,
    'T': True,
    'nH': True,
    'Z': True,
    'NHI': True,
    'x': False,
}
logscale_props = []
for prop_key, is_logscale in logscale.items():
    if is_logscale:
        logscale_props.append( prop_key )

property_labels = {
    'vlos': r'$v_{\rm LOS}$ [km/s]',
    'T': r'$\log T$ [K]',
    'nH': r'$\log n_{\rm H}$ [cm$^{-3}$]',
    'Z': r'$\log Z$ [$Z_{\odot}$]',
    'NHI': r'$\log N_{\rm H\,I}$ [cm$^{-2}$]',
    'x': r'$x$ [kpc]',
}
property_labels_no_units = {
    'vlos': r'$v_{\rm LOS}$',
    'T': r'T',
    'nH': r'$n_{\rm H}$',
    'Z': r'$Z$',
    'NHI': r'$N_{\rm H\,I}$',
    'x': r'$x$',
}
property_label_ends_1D = {
    'vlos': r' }{d v_{\rm LOS}}$',
    'T': r' }{d \log T}$',
    'nH': r' }{d \log n_{\rm H}}$',
    'Z': r' }{d \log Z}$',
    'NHI': r' }{d \log N_{\rm H\,I}}$',
    'x': r' }{dx}$',
}


weighting_labels = {
    'NHI': r'N_{\rm H\,I}',
    None: r'N_{\rm H}',
}

def property_labels_1D( prop_key, weighting ):
    
    return r'$\frac{ d ' + weighting_labels[weighting] + property_label_ends_1D[prop_key]
    
    
correlation_coefficient_property_labels = {}
for key, item in property_labels.items():
    unitless_label = item.split( '[' )[0]
    correlation_coefficient_property_labels[key] = r'$r($ ' + unitless_label + r'$)$'
correlation_coefficient_property_labels['all'] = r'$r($ all $)$'

# Argument for correlation coefficients, corresponding to names
correlation_coefficients = {
    'one-sided': {},
    'log one-sided': { 'logscale': True, 'subtract_mean': True },
    'two-sided': { 'one_sided': False, },
    'linear': { 'one_sided': False, 'subtract_mean': True },
    'log': { 'logscale': True, 'one_sided': False, 'subtract_mean': True },
}

lims = {
    'vlos': [ -75, 75 ],
    'T': [ 1e2, 2.5e6 ],
    'nH': [ 1e-7, 100 ],
    'Z': [ 1e-3, 30 ],
    'NHI': [ 1e9, 1e17 ],
    'x': [ -15, 15 ],
}
lims_1D = {
    # 'vlos': [ 3e9, 1e19 ],
    'vlos': [ 1e10, 1e18 ],
    'T': [ 1e12, 3e20 ],
    'nH': [ 1e12, 1e20 ],
    'Z': [ 1e12, 1e20 ],
    'NHI': [ 1e12, 3e20 ],
    'x': [ 3e9, 1e19 ],
}
lims_zoomed = {
    'vlos': [ -70, 70 ],
    'T': [ 10**2.5, 2.5e6 ],
    'nH': [ 10**-5, 10 ],
    'Z': [ 10**-2.5, 10**0.75 ],
    'NHI': [ 1e9, 1e17 ],
    'x': [ -15, 15 ],
}
autolims = {
    'vlos': False,
    'T': False,
    'nH': False,
    'Z': False,
    'NHI': False,
    'x': False,
}

# # Figure dimensions
# figure_width = 3.376 # Default figure width in inches; MNRAS column width
# # figure_width = 8. # Default figure width
# figure_height = figure_width
# # figure_height = figure_width / 2.
# max_figure_height = 9.437 # Text height for MNRAS
# large_fontsize = 14.4
# normal_fontsize = 12
# small_fontsize = 10.95
# footnote_fontsize = 10
lighter_textcolor = '0.4'
lightest_textcolor = '0.6'
# limits_whitespace = 0.05

# Plot elements
violin_width = 0.75 # In units of distance between violins

def percentile_str_fn( fraction ):
    return '{:.1f}'.format( fraction * 100 )

identifiers_to_slnums = {
    'r1_0.6000_0.6000_0.2500_r2_0.6000_0.6000_0.7500': '00',
    'r1_0.8000_0.4000_0.2500_r2_0.8000_0.4000_0.7500': '01',
    'r1_0.2000_0.6000_0.2500_r2_0.2000_0.6000_0.7500': '02',
    'r1_0.8000_0.5000_0.2500_r2_0.8000_0.5000_0.7500': '03',
    'r1_0.4000_0.6000_0.2500_r2_0.4000_0.6000_0.7500': '04',
    'r1_0.8000_0.4500_0.2500_r2_0.8000_0.4500_0.7500': '05',
    'r1_0.8000_0.5500_0.2500_r2_0.8000_0.5500_0.7500': '06',
    'r1_0.4000_0.4500_0.2500_r2_0.4000_0.4500_0.7500': '07',
    'r1_0.4000_0.5500_0.2500_r2_0.4000_0.5500_0.7500': '08',
    'r1_0.8000_0.6000_0.2500_r2_0.8000_0.6000_0.7500': '09',
    'r1_0.2000_0.4000_0.2500_r2_0.2000_0.4000_0.7500': '10',
    'r1_0.2000_0.5000_0.2500_r2_0.2000_0.5000_0.7500': '11',
    'r1_0.6000_0.5000_0.2500_r2_0.6000_0.5000_0.7500': '12',
    'r1_0.6000_0.4000_0.2500_r2_0.6000_0.4000_0.7500': '13',
    'r1_0.6000_0.5500_0.2500_r2_0.6000_0.5500_0.7500': '14',
    'r1_0.6000_0.4500_0.2500_r2_0.6000_0.4500_0.7500': '15',
    'r1_0.2000_0.4500_0.2500_r2_0.2000_0.4500_0.7500': '16',
    'r1_0.2000_0.5500_0.2500_r2_0.2000_0.5500_0.7500': '17',
    'r1_0.4000_0.4000_0.2500_r2_0.4000_0.4000_0.7500': '18',
    'r1_0.4000_0.5000_0.2500_r2_0.4000_0.5000_0.7500': '19'
}
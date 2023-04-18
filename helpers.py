import numpy as np

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

#############################################################
# Properties of images Nir sent
#############################################################

colorbar_loc = [[804, 40], [839, 482]]

img_areas = [
    [ [ 189, 39 ], [ 485, 484 ], ],
    [ [ 496, 39 ], [ 792, 484 ], ],
]

grid_coords = [
    # left panel
    [
        # x coords and widths
        [
            ( 188, 1 ),
            ( 202, 2 ),
            ( 217, 2 ),
            ( 232, 2 ),
            ( 246, 2 ),
            ( 261, 2 ),
            ( 276, 2 ),
            ( 291, 2 ),
            ( 306, 2 ),
            ( 321, 2 ),
            ( 336, 2 ),
            ( 350, 2 ),
            ( 365, 2 ),
            ( 380, 2 ),
            ( 395, 2 ),
            ( 410, 2 ),
            ( 425, 2 ),
            ( 439, 2 ),
            ( 454, 2 ),
            ( 469, 2 ),
            ( 484, 1 ),
        ],
        # y coords and widths
        [
            ( 38, 1 ),
            ( 53, 2 ),
            ( 68, 2 ),
            ( 82, 2 ),
            ( 97, 2 ),
            ( 112, 2 ),
            ( 127, 2 ),
            ( 142, 2 ),
            ( 156, 2 ),
            ( 171, 2 ),
            ( 186, 2 ),
            ( 201, 2 ),
            ( 216, 2 ),
            ( 230, 2 ),
            ( 245, 2 ),
            ( 260, 2 ),
            ( 275, 2 ),
            ( 290, 2 ),
            ( 304, 2 ),
            ( 319, 2 ),
            ( 334, 2 ),
            ( 349, 2 ),
            ( 364, 2 ),
            ( 378, 2 ),
            ( 393, 2 ),
            ( 408, 2 ),
            ( 423, 2 ),
            ( 437, 2 ),
            ( 452, 2 ),
            ( 467, 2 ),
            ( 483, 1 ),
        ],
    ],
    [
        [
            ( 495, 1 ),
            ( 509, 2 ),
            ( 524, 2 ),
            ( 539, 2 ),
            ( 553, 2 ),
            ( 568, 2 ),
            ( 583, 2 ),
            ( 598, 2 ),
            ( 613, 2 ),
            ( 628, 2 ),
            ( 643, 2 ),
            ( 657, 2 ),
            ( 672, 2 ),
            ( 687, 2 ),
            ( 702, 2 ),
            ( 717, 2 ),
            ( 732, 2 ),
            ( 746, 2 ),
            ( 761, 2 ),
            ( 776, 2 ),
            ( 791, 1 ),
        ],
        [
            ( 38, 1 ),
            ( 53, 2 ),
            ( 68, 2 ),
            ( 82, 2 ),
            ( 97, 2 ),
            ( 112, 2 ),
            ( 127, 2 ),
            ( 142, 2 ),
            ( 156, 2 ),
            ( 171, 2 ),
            ( 186, 2 ),
            ( 201, 2 ),
            ( 216, 2 ),
            ( 230, 2 ),
            ( 245, 2 ),
            ( 260, 2 ),
            ( 275, 2 ),
            ( 290, 2 ),
            ( 304, 2 ),
            ( 319, 2 ),
            ( 334, 2 ),
            ( 349, 2 ),
            ( 364, 2 ),
            ( 378, 2 ),
            ( 393, 2 ),
            ( 408, 2 ),
            ( 423, 2 ),
            ( 437, 2 ),
            ( 452, 2 ),
            ( 467, 2 ),
            ( 483, 1 ),
        ],
    ],
]
        
coords_first_dash_all = np.array([
    [ [ 333, 39 ], [ 340, 52 ], ],
    [ [ 640, 39 ], [ 647, 52 ], ],
])
coords_second_dash_all = np.array([
    [ [ 333, 74 ], [ 340, 100 ], ],
    [ [ 640, 74 ], [ 647, 100 ], ],
])

# Left, top, right, bottom
crop = [ [ 105, 7 ], [ 943, 561 ], ]

#############################################################
# Properties of old images Nir sent
#############################################################

# colorbar_loc = [[1016, 51], [1051, 493]]

# img_areas = [
#     [ [ 117, 41 ], [ 557, 481 ], ],
#     [ [ 566, 41 ], [ 1006, 481 ], ],
# ]

# grid_coords = [
#     # left panel
#     [
#         # x coords and widths
#         [
#             ( 117, 1 ),
#             ( 139, 2 ),
#             ( 161, 2 ),
#             ( 183, 2 ),
#             ( 204, 2 ),
#             ( 226, 2 ),
#             ( 248, 2 ),
#             ( 270, 2 ),
#             ( 292, 2 ),
#             ( 314, 2 ),
#             ( 336, 2 ),
#             ( 357, 2 ),
#             ( 379, 2 ),
#             ( 401, 2 ),
#             ( 423, 2 ),
#             ( 445, 2 ),
#             ( 467, 2 ),
#             ( 488, 2 ),
#             ( 510, 2 ),
#             ( 532, 2 ),
#             ( 555, 2 ),
#         ],
#         # y coords and widths
#         [
#             ( 41, 1 ),
#             ( 63, 2 ),
#             ( 85, 2 ),
#             ( 107, 2 ),
#             ( 129, 2 ),
#             ( 151, 2 ),
#             ( 172, 2 ),
#             ( 194, 2 ),
#             ( 216, 2 ),
#             ( 238, 2 ),
#             ( 260, 2 ),
#             ( 282, 2 ),
#             ( 304, 2 ),
#             ( 326, 2 ),
#             ( 348, 2 ),
#             ( 369, 2 ),
#             ( 391, 2 ),
#             ( 413, 2 ),
#             ( 435, 2 ),
#             ( 457, 2 ),
#             ( 479, 2 ),
#         ],
#     ],
#     [
#         [
#             ( 566, 1 ),
#             ( 588, 2 ),
#             ( 610, 2 ),
#             ( 632, 2 ),
#             ( 653, 2 ),
#             ( 675, 2 ),
#             ( 697, 2 ),
#             ( 719, 2 ),
#             ( 741, 2 ),
#             ( 763, 2 ),
#             ( 785, 1 ),
#             ( 806, 2 ),
#             ( 828, 2 ),
#             ( 850, 2 ),
#             ( 872, 2 ),
#             ( 894, 2 ),
#             ( 916, 2 ),
#             ( 937, 2 ),
#             ( 959, 2 ),
#             ( 981, 2 ),
#             ( 1004, 2 ),
#         ],
#         [
#             ( 41, 1 ),
#             ( 63, 2 ),
#             ( 85, 2 ),
#             ( 107, 2 ),
#             ( 129, 2 ),
#             ( 151, 2 ),
#             ( 172, 2 ),
#             ( 194, 2 ),
#             ( 216, 2 ),
#             ( 238, 2 ),
#             ( 260, 2 ),
#             ( 282, 2 ),
#             ( 304, 2 ),
#             ( 326, 2 ),
#             ( 348, 2 ),
#             ( 369, 2 ),
#             ( 391, 2 ),
#             ( 413, 2 ),
#             ( 435, 2 ),
#             ( 457, 2 ),
#             ( 479, 2 ),
#         ],
#     ],
# ]
        
# coords_first_dash_all = np.array([
#     [ [ 333, 42 ], [ 340, 49 ], ],
#     [ [ 782, 42 ], [ 789, 49 ], ],
# ])
# coords_second_dash_all = np.array([
#     [ [ 333, 71 ], [ 340, 97 ], ],
#     [ [ 782, 71 ], [ 789, 97 ], ],
# ])
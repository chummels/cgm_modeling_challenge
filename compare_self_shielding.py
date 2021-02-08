import yt
import trident
import unyt as u
import numpy as np
from numpy.random import uniform
import sys
import h5py as h5
import os
from matplotlib import pyplot as plt

'''
This program reads in the N density, temperature, metallicity, and redshift
values from the observers_file.h5 and calculates column density values for 
the various COS ions using the non-self-shielding ion_balance data table.

It then compares these new values with the results from the self-shielding 
ion_balance data table outputs, since those were the ones used in the 
calculation given to the observers.  It plots up the results of these
column density values for each ion to show if there are any obvious trends
for sightline 1, 2, 6, & 7, since the observers complained they had a hard
time making cloudy models to fit those sightlines.

USAGE:
$ python compare_SS.py observers_file.h5
'''

def input_observers_file(filename, ion_fields, ds_fields):
    f = h5.File(filename, 'r')

    # column_arr is an array of n_fields x n_rays
    column_arr = np.empty([n_fields, 10], dtype='float')

    # populate column_arr from HDF5 file
    for j,field in enumerate(ion_fields):
        column_arr[j][:] = f[field][:]

    # ds_arr is an array of 
    # [H_density, density, temp, metal, HI_column, length, redshift] x n_rays
    ds_arr = np.empty([7, 10], dtype='float')

    # populate ds_arr from HDF5 file
    for j,field in enumerate(ds_fields):
        ds_arr[j][:] = f[field][:]
    
    return column_arr, ds_arr

def print_dataset(ds, ions, fields):
    '''
    Print out relevant one zone properties and ion column densities to STDOUT
    '''
    # Print out our Ion column densities to STDOUT
    print("\nIon column densities:")
    for j,field in enumerate(fields):
        print("%s = %4.2g cm^-2" % (ions[j], ds.r[('gas', field)] * 
                                    ds.r[('gas', 'dl')]))

    m_hydrogen = 1.6605402e-24 * u.g
    # Print out our fluid values to STDOUT
    print('\nOne-zone dataset values:')
    print('''
density_H =   %4.2g cm^-3
density =     %4.2g g*cm^-3
temperature = %4.2g K
metallicity = %4.2g Zsun
HI_column   = %4.2g cm^-2
length =      %4.2g kpc
''' % (ds.r[('gas', 'density')] / m_hydrogen,
       ds.r[('gas', 'density')], 
       ds.r[('gas', 'temperature')], 
       ds.r[('gas', 'metallicity')],
       ds.r[('gas', 'H_p0_number_density')] * ds.r[('gas', 'dl')],
       ds.r[('gas', 'dl')].to('kpc')))

def store_dataset(ds_id, ds, ions, fields, column_arr, ds_arr):
    '''
    Store relevant one zone properties and ion column densities to 
    column_arr and ds_arr arrays.
    '''
    # column density info stored to array in order of "fields" list
    for j,field in enumerate(fields):
        column_arr[j, ds_id] = ds.r[('gas', field)] * ds.r[('gas', 'dl')]

    # dataset info stored to array in order of: 
    # density_H, density, temp, metallicity, HI_column, length, redshift
    # ("ds_props" list)
    ds_arr[:, ds_id] = [ds.r[('gas', 'density')] / m_hydrogen,
                        ds.r[('gas', 'density')], 
                        ds.r[('gas', 'temperature')], 
                        ds.r[('gas', 'metallicity')],
                        ds.r[('gas', 'H_p0_number_density')] * ds.r[('gas', 'dl')],
                        ds.r[('gas', 'dl')].to('kpc'),
                        redshift]

def save_file_for_observers(column_arr, ions):
    '''
    Save relevant ion column densities to HDF5 file observers
    '''
    # Initialize the output file
    f = h5.File('observers_file.h5','w')

    for j,ion in enumerate(ions):
        h5ds = f.create_dataset(ion, data=column_arr[j, :])
        h5ds.attrs.create('units', 'cm**-2')
    f.close()

def save_file_for_theorists(column_arr, ds_arr, ions):
    '''
    Save relevant one zone properties and ion column densities to HDF5
    file for theorists
    '''
    # Initialize the output file
    f = h5.File('theorists_file.h5','w')

    for j,ion in enumerate(ions):
        h5ds = f.create_dataset(ion, data=column_arr[j, :])
        h5ds.attrs.create('units', 'cm**-2')

    for j,ds_property in enumerate(ds_props):
        h5ds = f.create_dataset(ds_property, data=ds_arr[j, :])
        h5ds.attrs.create('units', ds_props_units[j])
    f.close()
   
if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.exit('Usage: $ python compare_SS.py observers_file.h5')
    fn = sys.argv[1]

    n_rays = 10
    ions = ['H I', 'O I', 'C II', 'C III', 'N II', 'N III', 'Si II', 'Si III', 'Si IV', 'N V', 'O VI']
    fields = ['H_p0_number_density', 
            'O_p0_number_density',
            'C_p1_number_density',
            'C_p2_number_density',
            'N_p1_number_density',
            'N_p2_number_density',
            'Si_p1_number_density',
            'Si_p2_number_density',
            'Si_p3_number_density',
            'N_p4_number_density',
            'O_p5_number_density']
    n_fields = len(fields)

    ds_props = ['H_density', 'density', 'temperature', 'metallicity', 'HI_column', 'length', 'redshift']
    ds_props_units = ['cm**-3', 'g*cm**-3', 'K', 'Zsun', 'cm**-2', 'kpc', ''] 

    m_hydrogen = 1.6605402e-24 * u.g
    redshift = 0.25

    # Read in values from HDF5 file for dataset properties and for 
    # ion column densities calculated with self-shielding table
    column_arr_old, ds_arr_old = input_observers_file(fn, ions, ds_props)

    # Initialize arrays to store all the column density data and field 
    # information for the datasets:

    # column_arr is an array of n_fields x n_rays
    column_arr = np.empty([n_fields, n_rays], dtype='float')

    # ds_arr is an array of 
    # [density_H, density, temp, metal, HI_column, length, redshift] x n_rays
    ds_arr = np.empty([7, n_rays], dtype='float')
    
    # Step through each of these arrays one at a time to select out our randomly
    # sampled densities, temperatures, metallicities, and HI_column_densities
    # to calculate one-zone dataset

    for i in range(n_rays):
    
        # First, let's create a one-zone dataset for our desired density,
        # temperature, metallicity, and redshift, drawing from the old values
        # in the HDF5 file.
    
        ray = trident.make_onezone_ray(density=ds_arr_old[1][i] * u.g * (u.cm)**(-3),
                                    temperature=ds_arr_old[2][i] * u.K,
                                    metallicity=ds_arr_old[3][i] * u.Zsun,
                                    length=ds_arr_old[5][i] * u.kpc,
                                    redshift=ds_arr_old[6][i],
                                    filename='ray.h5')
        trident.add_ion_fields(ray, ions=ions)
    
        # Print out the dataset to STDOUT
        print_dataset(ray, ions, fields)

        # Store new data in column_arr and ds_arr
        store_dataset(i, ray, ions, fields, column_arr, ds_arr)
        
    # Make a plot comparing the column densities for each ion from the 
    # "old" data from the HDF5 file (self shielding) vs the "new" data
    # using the non-SS ion balance table
    
    fig, axs = plt.subplots(6, 2)
    for j, ion in enumerate(ions):
        #import pdb; pdb.set_trace()
        x = int(j / 2)
        y = j % 2
        x_axis = range(len(ions))
        axs[x, y].plot(np.log10(column_arr[j,:]), 'ko') # Black Non-SS
        axs[x, y].plot(np.log10(column_arr_old[j,:]), 'bo') # Blue SS
        #axs[x, y].semilogy(x_axis, column_arr[j,:])
        axs[x, y].text(0.8, 0.8, ion, transform=axs[x,y].transAxes)

    axs[5,1].text(0.1, 0.5, 'Self-Shield', color='blue')
    axs[5,1].text(0.5, 0.5, 'No Self-Shield', color='black')
    for ax in axs.flat:
        ax.label_outer()
    fig.tight_layout()
    plt.savefig('plot.pdf')

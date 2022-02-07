import yt
import trident
import unyt as u
import numpy as np
from numpy.random import uniform
import sys
import h5py as h5
import os

'''
Run this code from the command line to generate 10 one-zone datasets as well
as their accompanying ray data and column density values for ions visible
by COS at z=0.25.  

For each dataset, the code will prompt you to accept it before saving it to 
file.  Be careful to examine the length of the one-zone dataset to determine 
whether you actually want to keep it or not (e.g., too large >1 Mpc or too 
small <1 kpc may not be useful).

USAGE:
$ python one_zone.py
'''

# Solar metallicity
# Report metallicities in fractional form when possible, but set solar = 0.014 otherwise.

# Ionization Model
# Haardt-Madau2012 w/SS for first pass. Make sure all use the same background for second pass.

# First Pass
# Mock CGM
# 10 individual Trident clouds with randomly drawn metallicity, density, temperature.

# Sample randomly these intervals:
# Metallicities .01 Zsun to 1.5 Zsun.
# Densities 1e-6 to 0.1 cm^-3.
# Temperature 1e4 to 1e6 K.

# Redshift
# z=0.25

# Ions
# ions present in COS-Halos
# H I, O I, C II, C III, N II, N III, Si II, Si III, Si IV, N V, O VI

# Oscillator Strengths
# Also should be consistent for the second pass.
# Use lines.txt from Trident source

# Number of Sightlines
# 10

# Observer Instrument
# COS G130M

# Column Density Error
# Draw errors from COS-Halos distribution of errors for ions.
# From Tumlinson+ 2013 Table 5, H I errors are all 0-0.1 in log space:
# e.g., log(N_HI) = 16 +- 0.1
# Other ion errors vary as Werk+ 2013 Table 4: 
# https://iopscience.iop.org/0067-0049/204/2/17/suppdata/apjs456058t4_mrt.txt

# Data Products
# Column densities with errors. After receiving results from observers, send them full spectra.

# Interpreting the Results
# What do we mean by the metallicity of the sightline?
# We’ll take the metallicities the observers give us and extract their definition. Possibilities include hydrogen (baryon) weighted metallicity, HI metallicity, etc.

#---------

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
    '''
    Main code generates a number of different datasets, asks for 
    confirmation by the user, then saves the relevant ones to an HDF5
    file for the observers (with just column density values) and to
    a different file for the theorists (with column density values and
    all dataset properties).
    '''

    # Number of desired rays
    n_rays = 10
    n_trials = 3*n_rays
    n_saved = 0
    
    # Randomly sample density, temperature, metallicity, and H I column density
    # in log space
    # H I column density is for calculating box size
    
    # densities in H atoms cm^-3
    density_min = 1e-6
    density_max = 1e0
    
    # create range of values and convert to g*cm^-3 
    density_H = 10.**uniform(low=np.log10(density_min), 
                        high=np.log10(density_max), 
                        size=n_trials) * (u.cm)**-3
    m_hydrogen = 1.6605402e-24 * u.g
    density = density_H * m_hydrogen # actual mass density goes into trident
    
    # temperatures in K
    temperature_min = 1e4
    temperature_max = 1e6
    temperature = 10.**uniform(low=np.log10(temperature_min), 
                            high=np.log10(temperature_max), 
                            size=n_trials) * u.K
    
    # metallicities in Z_sun
    metallicity_min = 1e-2
    metallicity_max = 1.5
    metallicity = 10.**uniform(low=np.log10(metallicity_min), 
                            high=np.log10(metallicity_max), 
                            size=n_trials) * u.Zsun
    
    # Desired HI column densities
    HI_column_min = 1e15
    HI_column_max = 1e17
    HI_column = 10.**uniform(low=np.log10(HI_column_min), 
                            high=np.log10(HI_column_max), 
                            size=n_trials) * (u.cm)**-2
    
    redshift = 0.25
    
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

    for i in range(n_trials):
    
        # First, let's create a one-zone dataset for our desired density,
        # temperature, metallicity, and redshift.  We'll arbitrarily set it to
        # be 1 kpc in width.  
        test_ds = trident.make_onezone_dataset(density=density[i],
                                        temperature=temperature[i],
                                        metallicity=metallicity[i],
                                        domain_width=1.*u.kpc)
        test_ds.current_redshift = redshift
    
        # Now let's add our desired ions to this dataset, using Trident's 
        # lookup table based on the Haardt-Madau 2012 UV background.
        trident.add_ion_fields(test_ds, ions=ions)
    
        # Since we now know the HI number density for this dataset, and we
        # have a desired HI column density from above (i.e., a LLS), we can divide 
        # these two to get a desired length for the dataset.
        length = HI_column[i] / test_ds.r[('gas', 'H_p0_number_density')][0]
    
        print("DEBUG: For an HI column of %s, we require a Pathlength of %s" % 
                (HI_column[i], length.to('kpc')))
    
        # Now that we have a length for our dataset, which will produce our 
        # desired HI column density to be a LLS, let's generate a one-zone
        # LightRay (skewer) using this length, density, temperature, & redshift.
        # And add the relevant ions to this dataset.
    
        ray = trident.make_onezone_ray(density=density[i],
                                    temperature=temperature[i],
                                    metallicity=metallicity[i],
                                    length=length,
                                    redshift=redshift,
                                    filename='ray.h5')
        trident.add_ion_fields(ray, ions=ions)
    
        # Print out the dataset to STDOUT
        print_dataset(ray, ions, fields)
        
        # Ask the user if they want to "keep" this dataset and store it.
        print("You have %i out of %i datasets stored." % (n_saved, n_rays))
        print("Would you like to save this dataset to the output HDF5 file? [Y]")
        value = input().rstrip()
        if (value == 'Y') or (value == '') or (value == 'y') or (value == 'Yes'):
            print("OK, keeping this dataset.\n")
            store_dataset(n_saved, ray, ions, fields, column_arr, ds_arr)
            os.rename('ray.h5', 'ray%04i.h5' % n_saved)
            n_saved += 1
        else:
            print("OK, ignoring this dataset.\n")
        if n_saved == n_rays:
            print("You have %i out of %i datasets stored." % (n_saved, n_rays))
            save_file_for_observers(column_arr, ions)
            save_file_for_theorists(column_arr, ds_arr, ions)
            print("Data stored to disk.")
            sys.exit()

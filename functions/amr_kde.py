
import numpy as np
from kde_map import kde_2d
from astroML.plotting import hist as h_ML


def age_met_rel(xarr, xsigma, yarr, ysigma, grid_step):
    """
    Generate a grid in the age-metallicity diagram.
    1- Obtain the 2D KDE of the age-metallicity parameters space.
    2- Obtain a unique [Fe/H] value for each age value in the grid, *weighted*
    by the KDE map.
    3- Obtain the error associated to that [Fe/H] value.

    See: http://math.stackexchange.com/q/1457390/37846
    """

    # Define 2D space extension where the KDE will be obtained.
    x_min, x_max = min(np.array(xarr) - np.array(xsigma)), \
        max(np.array(xarr) + np.array(xsigma))
    # These range defines the metallicity values (met_vals) that will be
    # weighted by the KDE below.
    y_min, y_max = min(np.array(yarr) - np.array(ysigma)), \
        max(np.array(yarr) + np.array(ysigma))

    # Grid density defined using the 'grid_step'.
    gd = int((y_max - y_min) / grid_step)

    # Generate metallicity values as in grid. Invert list so the weighted
    # average is obtained correctly.
    met_vals = np.linspace(y_min, y_max, gd)[::-1]
    age_vals = np.linspace(x_min, x_max, gd)

    # Obtain age-metallicity 2D KDE for the entire defined range.
    ext = [x_min, x_max, y_min, y_max]
    z = kde_2d(np.array(xarr), np.array(xsigma), np.array(yarr),
               np.array(ysigma), ext, gd)
    # Order KDE in age columns where each column is associated with an age.
    a_m_kde = zip(*z)

    # Obtain metallicity weighted average for each age value.
    met_weighted = [[], []]
    for age_col in a_m_kde:
        # Metallicity values given by the KDE for all the grid points defined
        # in the metallicity range, for a single age value.
        age_col = np.array(age_col)

        # Obtain weighted metallicity for this *single* age value.
        sum_age_col = sum(age_col)
        met_w = sum(met_vals * age_col) / sum_age_col
        met_weighted[0].append(met_w)

        # Obtain standard deviation.
        nume = sum(age_col * (met_w - met_vals) ** 2)
        deno = sum_age_col - (sum(age_col ** 2) / sum_age_col)
        stdev_met_w = np.sqrt(nume / deno)
        met_weighted[1].append(stdev_met_w)

    return age_vals, met_weighted


def feh_avrg(age_gyr, bn, age_vals, met_weighted):
    """
    1- Obtain bin edges for the entire age range.
    2- For each age range, obtain the average of the weighted [Fe/H],
       The associated age value is the mid point of the age range.
    3- Propagate errors to the representative [Fe/H] value for that age range.
    """

    age_vals_int, met_weighted_int, age_rang_MCs = [[], []], [[], []], [[], []]
    for k in [0, 1]:
        # import matplotlib.pyplot as plt
        # f, (ax1, ax2) = plt.subplots(1, 2)
        # ax1.scatter(age_vals[k], met_weighted[k][0])

        # Obtain bin edges for the entire age range.
        astroML_edges = h_ML(age_gyr[k][0], bins=bn, color='black',  # ax=ax2,
                             histtype='step', normed=True)
        # Bin width.
        delta = astroML_edges[1][1] - astroML_edges[1][0]
        # Extend one bin to the left and right.
        age_rang = [astroML_edges[1][0] - delta] + list(astroML_edges[1]) +\
            [astroML_edges[1][-1] + delta]
        # Print info to screen.
        gal = ['SMC', 'LMC']
        print('{}:  {} bins; {:.2f} bin width; {:.2f}-{:.2f}'
              ' limits'.format(gal[k], len(age_rang), delta, min(age_rang),
                               max(age_rang)))

        # Obtain average [Fe/H] in each age range. This is the [Fe/H] value
        # for that range.
        age_temp, met_temp, met_err_temp = [], [], []
        for i, edge in enumerate(age_rang[:-1]):
            # Define edges of bin.
            min_a, max_a = edge, age_rang[i+1]
            # Separate values for each interval in the age range, defined by
            # the edges obtained above.
            in_bin = [[], [], []]
            for a, m, e_m in zip(*[age_vals[k], met_weighted[k][0],
                                 met_weighted[k][1]]):
                if min_a <= a < max_a:
                    in_bin[0].append(a)
                    in_bin[1].append(m)
                    in_bin[2].append(e_m)

            try:
                # Age interval limits.
                a_0, a_1 = min(in_bin[0]), max(in_bin[0])
                # The x axis value (age) is the average for the interval.
                age_avrg = (a_0 + a_1)/2.
                # The y axis value ([Fe/H]) is the average for the interval.
                fe_h_avrg = np.mean(in_bin[1])
                # Store unique AMR x,y values.
                age_temp.append(age_avrg)
                met_temp.append(fe_h_avrg)
                # Obtain associated error for this average [Fe/H]_age value.
                # (Bevington and Robinson, 1992)
                met_err = np.sqrt((1./(len(in_bin[2])**2)) *
                           sum(np.asarray(in_bin[2])**2))
                met_err_temp.append(met_err)
            except:
                pass
        # plt.show()
        # Store AMR function values.
        age_vals_int[k], met_weighted_int[k], age_rang_MCs[k] =\
            age_temp, [met_temp, met_err_temp], age_rang

    return age_vals_int, met_weighted_int, age_rang_MCs


def get_amr_asteca(in_params):
    """
    Obtain AMR for both MCs. Steps:

    0- Filter OCs if necessary, for testing.
    1- Add old LMC OCs if necessary, for testing.
    2- Convert log(ages) to Age (Gyr) (same for errors)
    3- Define values for grid_step and binning. The latter is the one that will
       affect the AMR the most. The former just needs to be small enough to
       allowing sampling a fine grid in the age-metallicity space.
    4- Obtain equispaced age values in grid, and *weighted* [Fe/H]
       values in grid (age_vals, met_weighted).
    5- Call function to obtain an average [Fe/H] value for each age
       range, along with its error.
    """

    zarr, zsigma, aarr, asigma, gal_names = [
        in_params[_] for _ in ['zarr', 'zsigma', 'aarr', 'asigma',
                               'gal_names']]

    # k=0 --> ASteCA, k==1 --> Literature
    k = 0

    # First index j indicates the galaxy (0 for SMC, 1 for LMC), the second
    # index 0 indicates ASteCA values.
    # j=0 -> SMC, j=1 ->LMC
    age_gyr, age_vals, met_weighted, feh_f =\
        [[], []], [[], []], [[], []], [[], []]
    for j in [0, 1]:

        # Filter block.
        age_f, age_err_f, feh_err_f = [], [], []
        for v in zip(*[aarr[j][k], asigma[j][k], zarr[j][k], zsigma[j][k],
                       gal_names[j]]):
            # Filter cluster.
            include = False
            if k == 0:
                # To filter out HW85 and NGC294 (lowest metallicities)
                # if v[2] > -1.5:
                # To filter out the 4 LMC OCs with large ages and
                # metallicities.
                # if not (9.48 < v[0] < 9.6 and v[2] > -0.3):
                # To include all OCs.
                if True:
                    include = True
                    # Max limit on very large met errors.
                    feh_e = min(v[3], 2.)
            else:
                # Filter literature OCs with no [Fe/H] values.
                if v[3] > -10.:
                    include = True
                    # Min limit on 0. met errors.
                    feh_e = max(v[3], 0.05)

            if include:
                age_f.append(v[0])
                age_err_f.append(v[1])
                feh_f[j].append(v[2])
                feh_err_f.append(feh_e)
            else:
                print v

        # #####################################################################
        # # Add old LMC OCs taken from Piatti & Geisler (2013)
        # old_lmc_OCs = [[9.93, 10.09, 10.13, 10.11, 10.13, 10.09, 10.13,
        #                 10.15, 10.17, 10.09, 10.09, 10.09],
        #                [-1.049, -1.202, -1.369, -1.418, -1.62, -1.746,
        #                 -1.847, -1.865, -2.049, -1.997, -2.095, -2.196]]
        # if j == 1:
        #     age_f = age_f + old_lmc_OCs[0]
        #     feh_f[j] = feh_f[j] + old_lmc_OCs[1]
        #     # Add a reasonable but small error.
        #     age_err_f = age_err_f + [0.1]*len(old_lmc_OCs[0])
        #     feh_err_f = feh_err_f + [0.1]*len(old_lmc_OCs[0])
        # #####################################################################

        # Age expressed in Gyr units.
        a_gyr = 10 ** (np.asarray(age_f) - 9)
        e_a_gyr = np.log(10) * a_gyr * np.asarray(age_err_f)
        age_gyr[j] = [a_gyr, e_a_gyr]

        # Grid step.
        grid_step = 0.01

        # Weighted metallicity values for an array of ages.
        age_vals[j], met_weighted[j] = age_met_rel(
            age_gyr[j][0], age_gyr[j][1], feh_f[j], feh_err_f, grid_step)

    # THIS NUMBER WILL AFFECT THE SHAPE OF THE FINAL AMR.
    # Define method or number of bins for the age range.
    bn = 'knuth'
    # Obtain average [Fe/H] value for each age range.
    age_vals, met_weighted, age_rang_MCs = feh_avrg(
        age_gyr, bn, age_vals, met_weighted)
    #
    # # Replace the above by this line to skip the calculation of the average
    # # [Fe/H], and just keep the weighted values.
    # age_rang_MCs = [np.arange(-2., -1., 0.1), np.arange(-2., -1., 0.1)]

    amr_asteca = [age_vals, met_weighted, age_gyr, feh_f, age_rang_MCs, k]
    return amr_asteca

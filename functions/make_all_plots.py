
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.offsetbox as offsetbox

from functions.ra_dec_map import ra_dec_plots
from functions.kde_2d import kde_map


def as_vs_lit_plots(pl_params):
    '''
    Generate ASteCA vs literature values plots.
    '''
    gs, i, xmin, xmax, x_lab, y_lab, z_lab, xarr, xsigma, yarr, ysigma, \
        zarr, gal_name = pl_params

    xy_font_s = 18
    cm = plt.cm.get_cmap('RdYlBu_r')

    ax = plt.subplot(gs[i], aspect='equal')
    # ax.set_aspect('auto')
    plt.xlim(xmin, xmax)
    plt.ylim(xmin, xmax)
    if x_lab == '$(m-M)_{0;\,asteca}$':
        # Introduce random scatter.
        # 10% of axis ranges.
        xax_ext = (xmax - xmin) * 0.05
        rs_x = np.random.uniform(0., xax_ext, len(xarr))
        rs_y = np.random.uniform(0., xax_ext, len(xarr))
        xarr = xarr + rs_x
        yarr = yarr + rs_y
    plt.xlabel(x_lab, fontsize=xy_font_s)
    plt.ylabel(y_lab, fontsize=xy_font_s)
    ax.grid(b=True, which='major', color='gray', linestyle='--', lw=0.5,
            zorder=1)
    ax.minorticks_on()
    plt.plot([xmin, xmax], [xmin, xmax], 'k', ls='--')  # 1:1 line
    # Plot all clusters in dictionary.
    if x_lab == '$[Fe/H]_{asteca}$':
        # 1% of axis ranges.
        ax_ext = (xmax - xmin) * 0.01
        # Random scatter.
        rs_x = xarr + np.random.uniform(-ax_ext, ax_ext, len(xarr))
        rs_y = yarr + np.random.uniform(-ax_ext, ax_ext, len(xarr))
    else:
        rs_x, rs_y = xarr, yarr
    SC = plt.scatter(rs_x, rs_y, marker='o', c=zarr, s=70, lw=0.25, cmap=cm,
                     zorder=3)
    # Text box.
    ob = offsetbox.AnchoredText(gal_name, loc=4, prop=dict(size=xy_font_s))
    ob.patch.set(alpha=0.85)
    ax.add_artist(ob)
    # Only plot y error bar if it has a value assigned in the literature.
    for j, xy in enumerate(zip(*[xarr, yarr])):
        if ysigma:  # Check if list is not empty (radii list)
            if ysigma[j] > -99.:
                plt.errorbar(xy[0], xy[1], xerr=xsigma[j], yerr=ysigma[j],
                             ls='none', color='k', elinewidth=0.5, zorder=1)
            else:
                plt.errorbar(xy[0], xy[1], xerr=xsigma[j], ls='none',
                             color='k', elinewidth=0.5, zorder=1)
    # Position colorbar.
    the_divider = make_axes_locatable(ax)
    color_axis = the_divider.append_axes("right", size="5%", pad=0.1)
    # Colorbar.
    cbar = plt.colorbar(SC, cax=color_axis)
    zpad = 10 if z_lab == '$E_{(B-V)}$' else 5
    cbar.set_label(z_lab, fontsize=xy_font_s, labelpad=zpad)


def make_as_vs_lit_plot(galax, k, in_params):
    '''
    Prepare parameters and call function to generate ASteca vs literature
    SMC and LMC plots.
    '''

    zarr, zsigma, aarr, asigma, earr, esigma, darr, dsigma, rarr = \
        [in_params[_] for _ in ['zarr', 'zsigma', 'aarr', 'asigma', 'earr',
                                'esigma', 'darr', 'dsigma', 'rarr']]

    # Generate ASteca vs literature plots.
    fig = plt.figure(figsize=(17, 26))  # create the top-level container
    # gs = gridspec.GridSpec(2, 4, width_ratios=[1, 0.35, 1, 0.35])
    gs = gridspec.GridSpec(4, 2)

    if galax == 'SMC':
        dm_min, dm_max = 18.61, 19.39
    else:
        dm_min, dm_max = 18.11, 18.89

    as_lit_pl_lst = [
        [gs, 0, -2.4, 0.45, '$[Fe/H]_{asteca}$', '$[Fe/H]_{lit}$',
            '$log(age/yr)_{asteca}$', zarr[k][0], zsigma[k][0], zarr[k][1],
            zsigma[k][1], aarr[k][0], galax],
        [gs, 1, 5.8, 10.6, '$log(age/yr)_{asteca}$', '$log(age/yr)_{lit}$',
            '$E(B-V)_{asteca}$', aarr[k][0], asigma[k][0], aarr[k][1],
            asigma[k][1], earr[k][0], galax],
        [gs, 2, -0.04, 0.29, '$E(B-V)_{asteca}$', '$E(B-V)_{lit}$',
            '$log(age/yr)_{asteca}$', earr[k][0], esigma[k][0], earr[k][1],
            esigma[k][1], aarr[k][0], galax],
        [gs, 3, dm_min, dm_max, '$(m-M)_{0;\,asteca}$', '$(m-M)_{0;\,lit}$',
            '$log(age/yr)_{asteca}$', darr[k][0], dsigma[k][0], darr[k][1],
            dsigma[k][1], aarr[k][0], galax],
        [gs, 4, 1., 599., '$rad_{asteca} (px)$', '$rad_{lit} (px)$',
            '$log(age/yr)_{asteca}$', rarr[k][0], [], rarr[k][1], [],
            aarr[k][0], galax]
    ]
    #
    for pl_params in as_lit_pl_lst:
        as_vs_lit_plots(pl_params)

    # Output png file.
    fig.tight_layout()
    plt.savefig('figures/as_vs_lit_' + galax + '.png', dpi=300)


def kde_plots(pl_params):
    '''
    Generate KDE plots.
    '''
    gs, i, x_lab, y_lab, xarr, xsigma, yarr, ysigma, x_rang, y_rang = pl_params

    ext = [x_rang[0], x_rang[1], y_rang[0], y_rang[1]]

    # Generate maps.
    z = kde_map(np.array(xarr), np.array(xsigma), np.array(yarr),
                np.array(ysigma), ext)

    # Make plot.
    ax = plt.subplot(gs[i])
    xy_font_s = 18
    plt.xlabel(x_lab, fontsize=xy_font_s)
    plt.ylabel(y_lab, fontsize=xy_font_s)

    cm = plt.cm.get_cmap('RdYlBu_r')
    # cm = plt.cm.gist_earth_r
    ax.imshow(z, cmap=cm, extent=ext)
    ax.set_aspect('auto')
    # Errorbars.
    # plt.errorbar(xarr, yarr, xerr=xsigma, yerr=ysigma, fmt='none',
    #     elinewidth=0.4, color='k')
    # 1% of axis ranges.
    xax_ext = (ext[1] - ext[0]) * 0.01
    yax_ext = (ext[3] - ext[2]) * 0.01
    # Random scatter.
    rs_x = np.random.uniform(0., xax_ext, len(xarr))
    rs_y = np.random.uniform(0., yax_ext, len(xarr))
    # Clusters.
    plt.scatter(xarr + rs_x, yarr + rs_y, marker='*', color='#6b6868', s=40,
                lw=0.5, facecolors='none')
    ax.set_xlim(ext[0], ext[1])
    ax.set_ylim(ext[2], ext[3])


def make_kde_plots(galax, k, in_params):
    '''
    Prepare parameters and call function to generate SMC and LMC KDE plots.
    '''
    zarr, zsigma, aarr, asigma, earr, esigma, darr, dsigma, marr, msigma = \
        [in_params[_] for _ in ['zarr', 'zsigma', 'aarr', 'asigma', 'earr',
                                'esigma', 'darr', 'dsigma', 'marr', 'msigma']]

    fig = plt.figure(figsize=(14, 25))  # create the top-level container
    gs = gridspec.GridSpec(4, 2)       # create a GridSpec object

    # Define extension for each parameter range.
    age_rang, fe_h_rang, mass_rang = [6., 10.], [-2.4, 0.15], [-100., 10500.]
    if galax == 'SMC':
        E_bv_rang, dist_mod_rang = [-0.014, 0.16], [18.75, 19.25]
    else:
        E_bv_rang, dist_mod_rang = [-0.02, 0.31], [18.25, 18.75]

    kde_pl_lst = [
        [gs, 0, '$log(age/yr)$', '$[Fe/H]$', aarr[k][0], asigma[k][0],
            zarr[k][0], zsigma[k][0], age_rang, fe_h_rang],
        [gs, 1, '$log(age/yr)$', '$M\,(M_{\odot})$', aarr[k][0], asigma[k][0],
            marr[k][0], msigma[k][0], age_rang, mass_rang],
        [gs, 2, '$(m-M)_0$', '$E_{(B-V)}$', darr[k][0], dsigma[k][0],
            earr[k][0], esigma[k][0], dist_mod_rang, E_bv_rang],
        [gs, 3, '$M\,(M_{\odot})$', '$[Fe/H]$', marr[k][0], msigma[k][0],
            zarr[k][0], zsigma[k][0], mass_rang, fe_h_rang]
        # [gs, 4, '$log(age/yr)$', '$M\,(M_{\odot})$', aarr[k][0],
        # asigma[k][0], marr[k][0], msigma[k][0]],
        # [gs, 5, '$log(age/yr)$', '$M\,(M_{\odot})$', aarr[k][0],
        # asigma[k][0], marr[k][0], msigma[k][0]]
    ]
    #
    for pl_params in kde_pl_lst:
        kde_plots(pl_params)

    # Output png file.
    fig.tight_layout()
    plt.savefig('figures/as_kde_maps_' + galax + '.png', dpi=300)


def make_ra_dec_plots(in_params):
    '''
    Prepare parameters and call function to generate RA vs DEC positional
    plots for the SMC and LMC.
    '''

    ra, dec, zarr, aarr, earr, darr, marr, rad_pc = [
        in_params[_] for _ in ['ra', 'dec', 'zarr', 'aarr', 'earr', 'darr',
                               'marr', 'rad_pc']]

    # Put both SMC and LMC clusters into a single list.
    ra = ra[0] + ra[1]
    dec = dec[0] + dec[1]
    zarr = zarr[0][0] + zarr[1][0]
    aarr = aarr[0][0] + aarr[1][0]
    earr = earr[0][0] + earr[1][0]
    darr = darr[0][0] + darr[1][0]
    marr = marr[0][0] + marr[1][0]
    rad_pc = rad_pc[0] + rad_pc[1]

    fig = plt.figure(figsize=(20, 20))
    fig.clf()

    ra_dec_pl_lst = [
        [fig, 321, ra, dec, zarr, '$[Fe/H]$'],
        [fig, 322, ra, dec, aarr, '$log(age/yr)$'],
        [fig, 323, ra, dec, earr, '$E_{(B-V)}$'],
        [fig, 324, ra, dec, darr, '$(m-M)_0$'],
        [fig, 325, ra, dec, marr, '$M\,(M_{\odot})$'],
        [fig, 326, ra, dec, rad_pc, '$r_{clust}\,[pc]$']
    ]

    for pl_params in ra_dec_pl_lst:
        ra_dec_plots(pl_params)

    # Output png file.
    fig.tight_layout()
    plt.savefig('figures/as_RA_DEC.png', dpi=300)


def make_lit_ext_plot(in_params):
    '''
    Prepare parameters and call function to generate RA vs DEC positional
    plots for the SMC and LMC.
    '''

    earr, esigma, ext_sf, ext_mcev = [in_params[_] for _ in ['earr', 'esigma',
                                      'ext_sf', 'ext_mcev']]

    # Define values to pass.
    xmin, xmax = -0.02, 0.4
    x_lab, y_lab, z_lab = '$E(B-V)_{asteca}$', '$E(B-V)_{MCEV}$', \
        '$E(B-V)_{SF}$'

    fig = plt.figure(figsize=(16, 25))  # create the top-level container
    gs = gridspec.GridSpec(4, 2)       # create a GridSpec object

    ext_pl_lst = [
        # SMC
        [gs, 0, xmin, xmax, x_lab, y_lab, z_lab, earr[0][0], esigma[0][0],
            ext_mcev[0][0], ext_mcev[0][1], ext_sf[0][0], 'SMC'],
        # LMC
        [gs, 1, xmin, xmax, x_lab, y_lab, z_lab, earr[1][0], esigma[1][0],
            ext_mcev[1][0], ext_mcev[1][1], ext_sf[1][0], 'LMC']
    ]

    for pl_params in ext_pl_lst:
        as_vs_lit_plots(pl_params)

    # Output png file.
    fig.tight_layout()
    plt.savefig('figures/as_vs_lit_extin.png', dpi=300)


def wide_plots(pl_params):
    '''
    Generate plots for integrated colors, concentration parameter, and radius
    (in parsec) vs several parameters.
    '''
    gs, i, xmin, xmax, x_lab, y_lab, z_lab, xarr, xsigma, yarr, ysigma, zarr,\
        rad, gal_name = pl_params
    siz = np.asarray(rad) * 5

    xy_font_s = 16
    cm = plt.cm.get_cmap('RdYlBu_r')

    ax = plt.subplot(gs[i])
    # ax.set_aspect('auto')
    plt.xlim(xmin, xmax)
    # plt.ylim(xmin, xmax)
    plt.xlabel(x_lab, fontsize=xy_font_s)
    plt.ylabel(y_lab, fontsize=xy_font_s)
    ax.grid(b=True, which='major', color='gray', linestyle='--', lw=0.5,
            zorder=1)
    ax.minorticks_on()
    # Plot all clusters in dictionary.
    SC = plt.scatter(xarr, yarr, marker='o', c=zarr, s=siz, lw=0.25, cmap=cm,
                     zorder=3)
    # Plot x error bar.
    plt.errorbar(xarr, yarr, xerr=xsigma, ls='none', color='k',
                 elinewidth=0.4, zorder=1)
    # Plot y error bar if it is passed.
    if ysigma:
        plt.errorbar(xarr, yarr, yerr=ysigma, ls='none', color='k',
                     elinewidth=0.4, zorder=1)
    # Text box.
    ob = offsetbox.AnchoredText(gal_name, loc=2, prop=dict(size=xy_font_s))
    ob.patch.set(alpha=0.85)
    ax.add_artist(ob)
    # Position colorbar.
    the_divider = make_axes_locatable(ax)
    color_axis = the_divider.append_axes("right", size="2%", pad=0.1)
    # Colorbar.
    cbar = plt.colorbar(SC, cax=color_axis)
    zpad = 10 if z_lab == '$E_{(B-V)}$' else 5
    cbar.set_label(z_lab, fontsize=xy_font_s, labelpad=zpad)


def make_int_cols_plot(in_params):
    '''
    Prepare parameters and call function to generate integrated color vs Age
    (colored by mass) plots for the SMC and LMC.
    '''

    aarr, asigma, marr, int_colors, rad_pc = [
        in_params[_] for _ in ['aarr', 'asigma', 'marr', 'int_colors',
                               'rad_pc']]

    # Define values to pass.
    xmin, xmax = 6.5, 9.95
    x_lab, y_lab, z_lab = '$log(age/yr)_{asteca}$', \
        '$(C-T_{1})_{0;\,asteca}$', '$M\,(M_{\odot})$'

    fig = plt.figure(figsize=(16, 25))  # create the top-level container
    gs = gridspec.GridSpec(4, 1)       # create a GridSpec object

    ext_pl_lst = [
        # SMC
        [gs, 0, xmin, xmax, x_lab, y_lab, z_lab, aarr[0][0], asigma[0][0],
            int_colors[0], [], marr[0][0], rad_pc[0], 'SMC'],
        # LMC
        [gs, 1, xmin, xmax, x_lab, y_lab, z_lab, aarr[1][0], asigma[1][0],
            int_colors[1], [], marr[1][0], rad_pc[1], 'LMC']
    ]

    for pl_params in ext_pl_lst:
        wide_plots(pl_params)

    # Output png file.
    fig.tight_layout()
    plt.savefig('figures/as_integ_colors.png', dpi=300)


def make_concent_plot(in_params):
    '''
    Generate ASteCA concentration parameter (cp) plots, where:
    cp = n_memb / (r_pc **2)
    '''

    zarr, zsigma, aarr, asigma, marr, rad_pc, n_memb, rad_pc = [
        in_params[_] for _ in ['zarr', 'zsigma', 'aarr', 'asigma', 'marr',
                               'rad_pc', 'n_memb', 'rad_pc']]

    # Calculate the 'concentration parameter' as the approximate number of
    # (structural) members divided by the area of the cluster in parsecs.
    conc_p = [[], []]
    for j in [0, 1]:
        conc_p[j] = np.asarray(n_memb[j]) / \
            (np.pi * np.asarray(rad_pc[j]) ** 2)

    # Define values to pass.
    xmin, xmax = [6.5, -2.3], [10.4, 0.2]
    x_lab, y_lab, z_lab = ['$log(age/yr)_{asteca}$', '$[Fe/H]_{asteca}$'], \
        '$Concentration\,(N_{memb}/pc^{2})$', '$M\,(M_{\odot})$'

    fig = plt.figure(figsize=(16, 25))  # create the top-level container
    gs = gridspec.GridSpec(4, 1)       # create a GridSpec object

    conc_pl_lst = [
        # SMC
        [gs, 0, xmin[0], xmax[0], x_lab[0], y_lab, z_lab, aarr[0][0],
            asigma[0][0], conc_p[0], [], marr[0][0], rad_pc[0], 'SMC'],
        [gs, 1, xmin[1], xmax[1], x_lab[1], y_lab, z_lab, zarr[0][0],
            zsigma[0][0], conc_p[0], [], marr[0][0], rad_pc[0], 'SMC'],
        # LMC
        [gs, 2, xmin[0], xmax[0], x_lab[0], y_lab, z_lab, aarr[1][0],
            asigma[1][0], conc_p[1], [], marr[1][0], rad_pc[1], 'LMC'],
        [gs, 3, xmin[1], xmax[1], x_lab[1], y_lab, z_lab, zarr[1][0],
            zsigma[1][0], conc_p[1], [], marr[1][0], rad_pc[1], 'LMC']
    ]

    for pl_params in conc_pl_lst:
        wide_plots(pl_params)

    # Output png file.
    fig.tight_layout()
    plt.savefig('figures/concent_param.png', dpi=300)


def make_radius_plot(in_params):
    '''
    Plot radius (in pc) versus several parameters.
    '''

    zarr, zsigma, aarr, asigma, marr, msigma, n_memb, rad_pc, erad_pc = \
        [in_params[_] for _ in ['zarr', 'zsigma', 'aarr', 'asigma', 'marr',
                                'msigma', 'n_memb', 'rad_pc', 'erad_pc']]

    # Define values to pass.
    xmin, xmax = 0., 40.
    x_lab = '$R_{cl;\,asteca}\,(pc)$'
    y_lab = ['$log(age/yr)_{asteca}$', '$[Fe/H]_{asteca}$', '$M\,(M_{\odot})$']
    z_lab = ['$M\,(M_{\odot})$', '$log(age/yr)_{asteca}$']

    for i, gal_name in enumerate(['SMC', 'LMC']):

        fig = plt.figure(figsize=(16, 25))
        gs = gridspec.GridSpec(4, 1)

        rad_pl_lst = [
            [gs, 0, xmin, xmax, x_lab, y_lab[0], z_lab[0], rad_pc[i],
                erad_pc[i], aarr[i][0], asigma[i][0], marr[i][0], rad_pc[i],
                gal_name],
            [gs, 1, xmin, xmax, x_lab, y_lab[1], z_lab[0], rad_pc[i],
                erad_pc[i], zarr[i][0], zsigma[i][0], marr[i][0], rad_pc[i],
                gal_name],
            [gs, 2, xmin, xmax, x_lab, y_lab[2], z_lab[1], rad_pc[i],
                erad_pc[i], marr[i][0], msigma[i][0], aarr[i][0], rad_pc[i],
                gal_name]
        ]

        for pl_params in rad_pl_lst:
            wide_plots(pl_params)

        # Output png file.
        fig.tight_layout()
        plt.savefig('figures/as_rad_vs_params_' + gal_name + '.png', dpi=300)


def prob_vs_CI_plot(pl_params):
    '''
    Generate plots for KDE probabilities versus contamination indexes.
    '''
    gs, i, xmin, xmax, ymin, ymax, x_lab, y_lab, z_lab, xarr, yarr, zarr, \
        rad, gal_name = pl_params
    siz = np.asarray(rad) * 5

    xy_font_s = 16
    cm = plt.cm.get_cmap('RdYlBu_r')

    ax = plt.subplot(gs[i])
    # ax.set_aspect('auto')
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.xlabel(x_lab, fontsize=xy_font_s)
    plt.ylabel(y_lab, fontsize=xy_font_s)
    ax.grid(b=True, which='major', color='gray', linestyle='--', lw=0.5,
            zorder=1)
    ax.minorticks_on()
    # Plot all clusters in dictionary.
    SC = plt.scatter(xarr, yarr, marker='o', c=zarr, s=siz, lw=0.25, cmap=cm,
                     zorder=3)
    # Text box.
    ob = offsetbox.AnchoredText(gal_name, loc=2, prop=dict(size=xy_font_s))
    ob.patch.set(alpha=0.85)
    ax.add_artist(ob)
    # Position colorbar.
    the_divider = make_axes_locatable(ax)
    color_axis = the_divider.append_axes("right", size="2%", pad=0.1)
    # Colorbar.
    cbar = plt.colorbar(SC, cax=color_axis)
    zpad = 10 if z_lab == '$E_{(B-V)}$' else 5
    cbar.set_label(z_lab, fontsize=xy_font_s, labelpad=zpad)


def make_probs_CI_plot(in_params):
    '''
    Plot cluster's ASteCA probabilities versus contamination indexes.
    '''

    zarr, zsigma, aarr, asigma, marr, msigma, rad_pc, kde_prob, cont_ind = \
        [in_params[_] for _ in ['zarr', 'zsigma', 'aarr', 'asigma', 'marr',
                                'msigma', 'rad_pc', 'kde_prob', 'cont_ind']]

    # Define names of arrays being plotted.
    x_lab, y_lab, z_lab = '$CI_{asteca}$', '$prob_{asteca}$', \
        ['$log(age/yr)_{asteca}$', '$[Fe/H]_{asteca}$', '$M\,(M_{\odot})$',
            '$M\,(M_{\odot})$', '$log(age/yr)_{asteca}$']
    xmin, xmax, ymin, ymax = -0.01, 1.02, -0.01, 1.02

    fig = plt.figure(figsize=(16, 25))
    gs = gridspec.GridSpec(4, 2)

    prob_CI_pl_lst = [
        # SMC
        [gs, 0, xmin, xmax, ymin, ymax, x_lab, y_lab, z_lab[0], cont_ind[0],
            kde_prob[0], aarr[0][0], rad_pc[0], 'SMC'],
        [gs, 1, xmin, xmax, ymin, ymax, x_lab, y_lab, z_lab[1], cont_ind[0],
            kde_prob[0], zarr[0][0], rad_pc[0], 'SMC'],
        # LMC
        [gs, 2, xmin, xmax, ymin, ymax, x_lab, y_lab, z_lab[0], cont_ind[1],
            kde_prob[1], aarr[1][0], rad_pc[1], 'LMC'],
        [gs, 3, xmin, xmax, ymin, ymax, x_lab, y_lab, z_lab[1], cont_ind[1],
            kde_prob[1], zarr[1][0], rad_pc[1], 'LMC']
    ]

    for pl_params in prob_CI_pl_lst:
        prob_vs_CI_plot(pl_params)

    # Output png file.
    fig.tight_layout()
    plt.savefig('figures/as_prob_vs_CI.png', dpi=300)

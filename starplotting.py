import numpy as np
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_sun, Angle
from astropy.time import Time
from astropy.visualization import quantity_support
from matplotlib.ticker import FuncFormatter

def starplotting(ax, canvas, star_names, star_coords, observer_coords, observer_date, plot_axes):
    """
    Plots the altitude or parallactic angle of multiple stars over a night for a given observer location and date.
    
    Parameters:
        ax          : matplotlib Axes object
        canvas      : FigureCanvasTkAgg canvas to draw
        star_names  : list of star names
        star_coords : list of SkyCoord objects corresponding to star_names
        observer_coords: [[name, lat, lon, elevation]] 
        observer_date  : string "YYYY-MM-DD"
        plot_axes   : [x-axis choice, y-axis choice] (0=delta_midnight/UTC), (0=alt, 1=parallactic angle)
    """

    # ------------------------
    # Observer location and times
    observer = EarthLocation(
        lat=float(observer_coords[0][1]) * u.deg,
        lon=float(observer_coords[0][2]) * u.deg,
        height=float(observer_coords[0][3]) * u.m
    )
    
    linspace_size = 6000
    delta_midnight = np.linspace(-23, 23, linspace_size) * u.hour
    times = Time(observer_date + " 00:00:00") + delta_midnight
    midnight_ut = Time(observer_date + " 00:00:00")
    frame = AltAz(obstime=times, location=observer)

    # ------------------------
    # Compute altitudes and parallactic angles
    allstar_altaz = []  # List for altitude plotting
    pa_list = []        # List for parallactic angle plotting
    allstar_frames = [] # List to store unaltered frames for airmass calcing

    lst = times.sidereal_time('apparent', longitude=observer.lon)

    for star in star_coords:
        altaz = star.transform_to(frame)
        allstar_altaz.append(altaz.alt)
        allstar_frames.append(altaz) # To be used to calc airmass if selected
        
        ha = (lst - star.ra).wrap_at(180 * u.deg)
        
        # Need radians for proper parallactic angle calc
        lat_rad = observer.lat.to(u.rad)
        dec_rad = star.dec.to(u.rad)
        ha_rad  = ha.to(u.rad)
        
        # Parallactic angle calc
        pa_calc = np.arctan2(
                np.sin(ha_rad),
                np.tan(lat_rad) * np.cos(dec_rad) - np.sin(dec_rad) * np.cos(ha_rad)
                )
        pa_list.append(Angle(pa_calc).to(u.deg))

    # ------------------------
    # Sun altitude for shading night
    sun_altaz = get_sun(times).transform_to(frame)

    # ------------------------
    # Prepare x and y axes
    if plot_axes[0] == 0:
        xaxis = delta_midnight
        xlabel = "UTC"
    else:
        # Finally found my issue. Need to unwrap the lst for calcing the x-limits later
        lst_unwrapped = np.unwrap(lst.hour, period=24)
        xaxis = lst_unwrapped * u.hour
        xlabel = "Local Sidereal Time (hours)"
 
    if plot_axes[1] == 0:
        yaxis = allstar_altaz
        ylabel = "Altitude [deg]"
    elif plot_axes[1] == 1:
        yaxis = pa_list
        ylabel = "Parallactic Angle [deg]"
    elif plot_axes[1] == 2:
        # Convert altitude to airmass
        starairmasss_night = []
        for alt in allstar_frames:
            starairmasss_night.append(alt.secz)
        yaxis = starairmasss_night
        ylabel = "Airmass"
    #--------------------------------------------------------------------------------------------

    # Plot centering 
    # Get sun times for use in creating visuals
    sunaltazs = get_sun(times).transform_to(frame)
    
    # Find alt/az on certain date
    delta_midnight = np.linspace(-23, 23, linspace_size) * u.hour
    times = midnight_ut + delta_midnight
    frame = AltAz(obstime=times, location=observer)
    
    # Finding the delta_midnight indexes where the sun crosses the horizon
    sun_below = sunaltazs.alt < 0 * u.deg
    crossings = np.where(np.diff(sun_below.astype(int)) != 0)[0] #idk what this is doing but I copied it and works
    
        
    # Getting the sunset indexes for delta_midnight specifically
    sunsets = np.where((sunaltazs[:-1].alt > 0 * u.deg) & (sunaltazs[1:].alt < 0 * u.deg))[0]
    
    # Finding the sunset closest to the center, which would likely be the night for the date being looked up
    # Starting with the largest difference possible, comparing all the sunsets differences
    sunset_min_diff = linspace_size / 2 
    for y in range(len(sunsets)):
        sunset_diff = abs((linspace_size / 2) - sunsets[y])
        if sunset_min_diff > sunset_diff:
            sunset_min_diff = sunset_diff
            sunset_closest_diff_index = sunsets[y]
            
    # Indexes for delta_midnight
    sunset = sunset_closest_diff_index 
    sunrise = crossings[(y * 2) + 1]

    # ------------------------
    # Clear previous plot
    ax.clear()
    quantity_support()  
    # -------------------------

    # Recreate the annot after clearing
    ax.annot = ax.annotate("", xy=(0,0), xytext=(8,8), textcoords="offset points",
                           bbox=dict(boxstyle="round", fc="white", alpha=0.9),
                           annotation_clip=False
    )
    ax.annot.set_visible(False)
    
    # Recreate the cursor line after clearing
    ax.cursor_line = ax.axvline(color='red', linestyle='--', alpha=0.5)
    ax.cursor_line.set_visible(False)
    
    # Array for each star
    ax.hover_lines = []
    
    # Array for hover-over points
    scatter_points = []  

    # Setting up the probe for finding the values of which point is under the cursor
    for i, name in enumerate(star_names):
        line, = ax.plot(xaxis, yaxis[i], label=name)
        ax.hover_lines.append((line, name))
        # Add a few scatter points for hover (every 10th point)
        scatter = ax.scatter(xaxis[::10], yaxis[i][::10], s=50, alpha=0)
        scatter_points.append((scatter, name))
    #------------------------
    # Set up a second ax.annotate to hold the annotation box when frozen
    ax.frozen_annot = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                                  bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.9), 
                                  annotation_clip=False)
    ax.frozen_annot.set_visible(False)


    # ------------------------
    # Shade night and twilight
    # For airmass need to have a fill that doesn't use degrees
    if plot_axes[1] == 2:
        fill_top = 100
        fill_bottom = -100
    else:
        fill_top = 180*u.deg
        fill_bottom = -180*u.deg
        
    ax.fill_between(xaxis, fill_bottom, fill_top, sun_altaz.alt < 0*u.deg, color="0.5", zorder=0)
    ax.fill_between(xaxis, fill_bottom, fill_top, sun_altaz.alt < -18*u.deg, color="k", zorder=0)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # x-limits based on selection
    ax.set_xlim(xaxis[sunset] - (1 * u.hour), xaxis[sunrise] + (1 * u.hour))
    # Need to unwrap the lst after the limits are calcs. Will just change the numbers to be modulated to 24
    def lst_wrap_formatter(x, pos):
        # Format the new number as the modulo of x (all ticks), trunkated to have 0 decimals
        return f"{x % 24:.0f}"
    if plot_axes[0] == 1:
        # Apply the format to all ticks
        ax.xaxis.set_major_formatter(FuncFormatter(lst_wrap_formatter))
        
        
    
    # y-limitss based on selection
    if plot_axes[1] == 0:
        ax.set_ylim(0, 90)
    elif plot_axes[1] == 1:
        ax.set_ylim(-180, 180)
    elif plot_axes[1] == 2:
        ax.set_ylim(0, 4)
    ax.legend()
    ax.grid(True)

    # Marker to expand the point being shown
    ax.hover_markers = []
    
    # Create the hover circle for all the stars
    for i in star_names:
        m = ax.scatter([], [], s=70, color='yellow', edgecolor='black', zorder=10)
        m.set_visible(False)
        ax.hover_markers.append(m)
    # ------------------------
    # Store for hover
    ax.scatter_points = scatter_points
    ax.star_names = star_names

    canvas.draw()















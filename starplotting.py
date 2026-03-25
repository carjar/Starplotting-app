import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_body, get_sun, Angle
from astropy.time import Time
from astropy.visualization import quantity_support
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FormatStrFormatter

def starplotting(ax, canvas, star_names, star_coords, observer_coords, observer_date, plot_axes):
    # Get target from name lookup. Use exact coords if lookup fails
    # star_name = "M77"
    # star = SkyCoord.from_name(star_name)
    # m33 = SkyCoord(23.46206906, 30.66017511, unit="deg")
    
    
    # Get the coords of the observatory or location observing from. 
    observer = EarthLocation(lat=float(observer_coords[0][1]) * u.deg, lon=float(observer_coords[0][2]) * u.deg, height=float(observer_coords[0][3]) * u.m)
    utcoffset = -7 * u.hour  # MST
    lstoffset = 0

    # Midnight at locations time
    midnight = Time(observer_date + " 00:00:00") - utcoffset  
    midnight_ut = Time(observer_date + " 00:00:00")
    
    # Get alt/az for 100 points centered around midnight
    # frame_night = AltAz(obstime=midnight + delta_midnight, location=observer)
    # staraltazs_night = star.transform_to(frame_night)
    
    # Converting to airmass
    # starairmasss_night = staraltazs_night.secz
    
    # Plot airmass
    # with quantity_support():
    #     fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    #     ax.plot(delta_midnight, starairmasss_night)
    #     ax.set_xlim(-2, 10)
    #     ax.set_ylim(1, 4)
    #     ax.set_xlabel("Hours from EDT Midnight")
    #     ax.set_ylabel("Airmass [Sec(z)]")
    #     plt.draw()
    
    
    # Find alt/az on certain date
    linspace_size = 4000
    delta_midnight = np.linspace(-23, 23, linspace_size) * u.hour
    times = midnight_ut + delta_midnight
    frame = AltAz(obstime=times, location=observer)
    

    
    # Bringing in the list of stars instead of just one
    allstaraltaz = []
    for i in range(len(star_names)):
        allstaraltaz.append(star_coords[i].transform_to(frame))
        allstaraltaz[i] = allstaraltaz[i].alt
    
    # Get sun times for use in creating visuals
    sunaltazs = get_sun(times).transform_to(frame)


    # Overwrite for the x axis tick labels to be in 24h time instead of -12 to 12
    xlabels = (np.arange(13) * 2 - 12)
    for x in range(len(xlabels)):
        if xlabels[x] < 0:
            xlabels[x] += 24
    # xlabels *= u.hour

#--------------------------------------------------------------------------------------------

    # Plot centering
    # Finding the delta_midnight indexes where the sun crosses the horizon
    sun_below = sunaltazs.alt < 0 * u.deg
    crossings = np.where(np.diff(sun_below.astype(int)) != 0)[0] #idk what this is doing but it works
    
        
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
 
#--------------------------------------------------------------------------------------------

    # Calculating parallactic angle   
    # Starting with getting lst to then get hour angle. Can use this for the plot later
    pa = []
    for i in range(len(star_names)):
        lst = times.sidereal_time('apparent', longitude=observer.lon)
        ha = (lst - star_coords[i].ra).wrap_at(180 * u.deg)
        star_dec = star_coords[i].dec
        
        # Getting pa. The initial calculation returns radians which I want to be converted to degrees
        # I used the equation: q = arctan2(sin(H), tan(φ)·cos(δ) − sin(δ)·cos(H)). Sure hope it's correct
        pa_calc = np.arctan2(np.sin(ha), np.tan(observer.lat) * np.cos(star_dec) - np.sin(star_dec) * np.cos(ha))
        pa.append(Angle(pa_calc).to(u.deg))


#--------------------------------------------------------------------------------------------
      
    # Setting the axes
    # x-axis
    if plot_axes[0] == 0:
        xaxis = delta_midnight
    elif plot_axes[0] == 1:
        xaxis = lst
    elif plot_axes[0] == 2:
        xaxis = delta_midnight # Need to add local time later (maybe)
        
    # y-axis
    if plot_axes[1] == 0:
        yaxis = allstaraltaz
    elif plot_axes[1] == 1:
        yaxis = pa
    elif plot_axes[1] == 2:
        yaxis = allstaraltaz # Will add airmass later
    
    
    # Plot target height over the night
    with quantity_support():
        # fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        ax.clear()
        
        for x in range(len(allstaraltaz)):
            mappable = ax.scatter(                
                # delta_midnight,
                xaxis,
                # allstaraltaz[x].alt,
                # pa,
                yaxis[x],
                # c=allstaraltaz[x].az.value,
                label = star_names[x],
                lw=0,
                s=8,
                # cmap="viridis",
            )
        
#--------------------------------------------------------------------------------------------
        # Trying to rewrite the x labels to be scalable if I want to zoom to plot bounds
        midnight_local = Time(observer_date + " 00:00:00")
        # times_diff = ((times - midnight).sec) / 3600
       
            
        # Get current x limits
        # ax.set_xlim(-12 * u.hour, 12 * u.hour)
        # ax.set_xlim(twilight_start_time, twilight_end_time)
        tick_spacing = 2 * u.hour
        xmin, xmax = ax.get_xlim()
        
        # Convert to Quantity
        xmin = xmin * u.hour
        xmax = xmax * u.hour
        
        # Build tick positions dynamically
        ticks = np.arange(
            np.ceil(xmin.value / tick_spacing.value) * tick_spacing.value,
            xmax.value + tick_spacing.value,
            tick_spacing.value,
        ) # * u.hour
        
        ax.set_xticks(ticks * u.hour)
        
        # Convert delta_midnight offsets into actual clock times
        # tick_times = (midnight_local) + ticks 
        # tick_labels = tick_times.datetime
        
        # for t in range(len(tick_labels)):
            # tick_labels[t].datetime.hour
        ax.set_xticklabels(ticks)
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
#--------------------------------------------------------------------------------------------        

#--------------------------------------------------------------------------------------------


        # full night fill
        ax.fill_between(
            delta_midnight,
            -90 * u.deg,
            90 * u.deg,
            sunaltazs.alt < (-0 * u.deg),
            color="0.5",
            zorder=0,
        )
        # 18 deg twilight fill
        ax.fill_between(
            delta_midnight,
            -90 * u.deg,
            90 * u.deg,
            sunaltazs.alt < (-18 * u.deg),
            color="k",
            zorder=0,
        )
        # fig.colorbar(mappable).set_label("Azimuth [deg]")
        ax.legend(loc="upper left")
        # ax.set_xlim(-24 * u.hour, 24 * u.hour)
        ax.set_xlim(delta_midnight[sunset] - (1 * u.hour), delta_midnight[sunrise] + (1 * u.hour))
        # ax.set_xlim(0.3170792698174552 * u.hour, 14.659664916229055 * u.hour)
        # ax.set_xticks((np.arange(13) * 2 - 12) * u.hour)
        ax.set_ylim(-90 * u.deg, 90 * u.deg)
        ax.set_xlabel("UT (h)")
        ax.set_ylabel("Altitude [deg]")
        ax.grid(visible=True)
        # plt.xlim(-8 * u.hour, 8 * u.hour)
        # plt.draw()
        canvas.draw()






# Testing def

# import csv
# from matplotlib.figure import Figure
# from tkinter import ttk, Button, Label, Entry, Frame, Checkbutton
# import tkinter as tk  

# root = tk.Tk()
# root.geometry("1000x600")
# root.title("Star lookup")

# star_names = "M77"
# star_coords = SkyCoord.from_name(star_names)
# with open('observer_list.csv', newline='') as csvfile:
#     observer_locations = list(csv.reader(csvfile))
    
# observer_coords = []
# observer_coords.append(observer_locations[0])
# observer_date = "2026" + '-' + "02" + '-' + "19"

# fig = Figure()
# ax = fig.add_subplot(111)
# canvas = FigureCanvasTkAgg(fig, root)
# canvas.get_tk_widget().pack(side='right', anchor='ne')
# root.mainloop()

# starplotting(ax, canvas, star_names, star_coords, observer_coords, observer_date)















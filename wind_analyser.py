#!/usr/bin/env python3
# Georgii whether analyser
#30 May 2018

import csv
import numpy as np
import math
from matplotlib.collections import PatchCollection
from matplotlib.patches import Wedge
import matplotlib.pyplot as plt


maxwind = 14 #maximal wind speed im m/s for lists 
maxwind10 = maxwind*10
unification_factor = 2 # the precion of wind speed scale will be (1 / unification_factor) m/s scale.
#Possible values 1, 2, 5, 10

# There are 16 possible wind directions in the log (column 13): 
direction_names = {'N': 0, 'NNE': 1, 'NE': 2,  'ENE': 3,  'E': 4,  'ESE': 5,  'SE': 6,  'SSE': 7,
                   'S': 8, 'SSW': 9, 'SW': 10, 'WSW': 11, 'W': 12, 'WNW': 13, 'NW': 14, 'NNW': 15}
##################################################################################################

def delete_nulls_in_csv():  #original csv file contains null element because of unknown reason
    fi = open('meteo.csv', 'rb')
    next(fi) #skip header
    data = fi.read()
    fi.close()
    fo = open('meteo.csv', 'wb')
    fo.write(data.replace(b'\x00', b''))
    fo.close()
#################################################################################################
     
def main():
    data = []
    # the CSV log is stored in UTF-16 with tab separated columns
    with open('meteo.csv', newline='', encoding='utf-16') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            data.append(row)
           
    wind_list = [[0 for x in range(maxwind10)] for y in range(16)]
    gust_list = [[0 for x in range(maxwind10)] for y in range(16)]
    max_data_wind = 0.0 #maximal wind speed from the data
    max_data_gust = 0.0 #maximal wind speed from the data
    mean_speed = 0.0
    
    max_data_wind_direction = 0
    #print(len(wind_list))
       

    for j in range(0, len(data)):
        splitted_line = data[j]  # row is already split into columns
        try:
            # get direction as a number from column 11
            direction = int(direction_names[splitted_line[11]])
            # get wind speed from column 9
            speed = float(splitted_line[9])
            mean_speed += speed  # integrate all speed values
            # get gust speed from column 10

            gust = float(splitted_line[10])
            #search for maximal speed:
            if (speed>max_data_wind):
                    max_data_wind = speed
                    max_data_wind_direction = direction
            #search for maximal gust:
            if (gust>max_data_gust):         
                    max_data_gust = gust
            try: #update probability density 2D arrays
                wind_list[direction][round(speed*unification_factor)]+= 1
                gust_list[direction][round(gust*unification_factor)]+= 1
            except IndexError:
                print(f'IndexError in the line {j}, direction is {direction}, wind is {speed}')
        except ValueError:
            ''
        except KeyError:
            ''
    mean_speed = mean_speed/len(data)      
#----------------------------------------------------------------------------------------------
            # Creating arrays of sectors for plots
#----------------------------------------------------------------------------------------------            
    patches = []
    colors = []
    patches2 = []
    colors2 = []
    
    for speed in range(maxwind10):   
        for direction in range(16): 
            if (wind_list[direction][speed]>0): #wind
                patches += [Wedge((.0, .0), (speed/unification_factor), 22.5*(direction+3.5), 22.5*(direction+4.5), width=(1/unification_factor))]
                colors.append(math.log(wind_list[direction][speed],10))
            if (gust_list[direction][speed]>0): #gust
                patches2 += [Wedge((.0, .0), (speed/unification_factor), 22.5*(direction+3.5), 22.5*(direction+4.5), width=(1/unification_factor))]
                colors2.append(math.log(gust_list[direction][speed],10))
    
    #Creating a circular frame:
    patches.append(Wedge((.0, .0), max_data_wind*2, 0, 360, width=max_data_wind, label='fdg'))
    colors.append(max(colors))
    #Creating a circular frame:
    patches2.append(Wedge((.0, .0), max_data_gust*2, 0, 360, width=max_data_gust, label='fdg'))
    colors2.append(max(colors2))
    
#---------------------------------------------------------------------------------------------
#          Finally, plot all wedges
#---------------------------------------------------------------------------------------------
   
    ax = plt.subplot(1,2,1) #Wind first 
    
    p = PatchCollection(patches, alpha=1, cmap='YlOrBr')
    p.set_array(np.array(colors))
    ax.add_collection(p)
    
    
    cbar = plt.colorbar(p, ax=ax)
    cbar.set_label('Probability density (R.U), log scale')
    ax.set_title('Wind Speed Probability')

    ax.set_xlabel("West - East speed, m/s")

    ax.set_ylabel("Sounth - North speed, m/s")
    ax.grid(linestyle='-', linewidth=.4)
    plt.ylim([-max_data_wind,max_data_wind])
    plt.xlim([-max_data_wind,max_data_wind])
    plt.text(-0.5, max_data_wind-2, 'N', fontsize=15, color = 'tab:gray')
    plt.text(-0.5, -max_data_wind+1, 'S', fontsize=15, color = 'tab:gray')
    plt.text(-max_data_wind+1, -0.5, 'W', fontsize=15, color = 'tab:gray')
    plt.text(max_data_wind-2, -0.5, 'E', fontsize=15, color = 'tab:gray')
    
#------------------------------------------------------------------------------------------------   
    ax2 = plt.subplot(1,2,2) #Gust second
    
    p2 = PatchCollection(patches2, alpha=1, cmap='Blues')
    p2.set_array(np.array(colors2))
    ax2.add_collection(p2)
    
    cbar = plt.colorbar(p2, ax=ax2)
    cbar.set_label('Probability density (R.U), log scale')
    ax2.set_title('Gust Speed Probability')
    ax2.set_ylabel("Sounth - North speed, m/s")
    ax2.set_xlabel("West - East speed, m/s")
    ax2.grid(linestyle='-', linewidth=.4)
  
    plt.ylim([-max_data_gust,max_data_gust])
    plt.xlim([-max_data_gust,max_data_gust])
    
    plt.text(-0.5, max_data_gust-2, 'N', fontsize=15, color = 'tab:gray')
    plt.text(-0.5, -max_data_gust+1, 'S', fontsize=15, color = 'tab:gray')
    plt.text(-max_data_gust+1, -0.5, 'W', fontsize=15, color = 'tab:gray')
    plt.text(max_data_gust-2, -0.5, 'E', fontsize=15, color = 'tab:gray')
    
    plt.subplots_adjust(right = 1.8, top = 1.05) #set size for plots

    # Save the resulting figure to a file so it can be viewed later
    plt.savefig('wind_rose.png')
    plt.show()
  
#------------------------------------------------------------------------------------------------
#       Printing some numerical values  
    max_data_wind_direction_value = [key for key, value in direction_names.items() if value == max_data_wind_direction][0]
    print(f'Max wind speed is {max_data_wind} m/s in {max_data_wind_direction_value} direction')
    print(f'Mean absolute value of the wind speed is {mean_speed:.1f} m/s')
    print(f'Max gust speed is {max_data_gust} m/s')
    
if __name__ == '__main__': main()
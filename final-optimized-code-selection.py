#%%
import numpy as np
import matplotlib.pyplot as plt
import random as random
import time

#%%
#defining the function: 
start_time = time.time()

def Wright_Fisher_model(N, p0, generations, mu, v, a, ms, mt, b):
   
    p = np.full(a , p0)
    
    for i in range(generations):
        
        # describing fluctuating selection:
        s = np.random.normal(ms , np.sqrt(v), a) #s = sigma
        t = np.random.normal(mt , np.sqrt(v), a) #t = tau

        # main equation describing fluctuating selection:
        p = p +  (p * (1 - p) * (s - t)) / (1 + (p * s) + (t * (1 - p)))
        
        #check if selection coefficient is pushing too much, adjust p:    
        p[(p < 0)] = 0
        p[(p > 1)] = 1
        
        # Describing drift:
        allele_counts = np.random.binomial(2 * N, p)
        p = allele_counts / (2. * N)
                       
        #checking if frequency hits the boundry (0) and if a mutation is happening with rate mu:
        mutation_condition = (p == 0) & (np.random.rand(a) <= mu * 2 * N)
        p[mutation_condition] = 1 / N
         
        p[(p == 1)] = 0

    return p 

#initial value for describing phenomenon:
N = 1000
p0 = 0.01
generations = 10 * N
mu = 1 / (10 * N)

#initial value to decribe flactuating selection:
v_values = np.linspace(0, 1e-2, 10)
b_values = np.linspace(0, 2e-3, 10)

#%%
#Matrix to store results for vectorized bias and selective fluctuation:
a = 10**4
batch_size = 10**4
num_batches = a // batch_size
 
output_directory = r"C:\Users\Zahra\research codes -  fluctuating selection"

for i, v in enumerate(v_values):
    
    for j, b in enumerate(b_values):
        
        ms = [-b/2]
        mt = [b/2]
        
        for batch in range(num_batches):
                
            batch_a = Wright_Fisher_model(N, p0, generations, mu, v, a, ms, mt, b)
            
            output_filename = f"{output_directory}\\p_b{batch}_v={v}_b={b}.txt"
            
            np.savetxt(output_filename, batch_a, delimiter=',', fmt='%f')

#%%
#defining the analytical solution function: 
def r1(B):
    return (1 - (np.sqrt(1 + (4 / B))))/ 2

def r2(B):
    return (1 + (np.sqrt(1 + (4 / B)))) / 2

def k(B):
    return np.log(((1 - r1(B)) / (-r1(B))) * (r2(B) / (r2(B) - 1)))

def g(y, B):
    return np.log(((1 - r1(B)) / (y - r1(B))) * ((r2(B) - y) / (r2(B) - 1)))

def f1(y, B):
    return (2 / (k(B) * y * (1 - y))) * g(y, B)

#%%
#plotting process:
output_directory =  r"C:\Users\Zahra\research codes -  fluctuating selection"
a = 10**4
batch_size = 10**4
num_batches = a // batch_size

color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

for i, v in enumerate(v_values):
    
    color = color_cycle[i % len(color_cycle)]
        
    for batch in range(num_batches):
        
        loaded_data = np.loadtxt(f"{output_directory}\\p_b{batch}_v={v}_b={b}.txt", delimiter=',')

        # Define bin edges and compute the histogram:
        bin_width = np.linspace(((1 / N) + (1 /(2 * N))), 1, 101)
    
        counts, bins = np.histogram(loaded_data, bins=bin_width)
    
        bin_centers = (bins[:-1] + bins[1:]) / 2
    
        riemann_sum = np.sum(counts * (bin_centers[1] - bin_centers[0]))
    
        normalized_counts = counts / riemann_sum
    
        plt.plot(bin_centers, normalized_counts, color=color)
        
#%%
color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

for i, v in enumerate(v_values):
    
    color = color_cycle[i % len(color_cycle)]
    
    # Initialize an empty array to collect allele frequency data from all batches for each v:
    all_data = []

    for batch in range(num_batches):
        
        loaded_data = np.loadtxt(f"{output_directory}\\p_b{batch}_v={v}_b={b}.txt", delimiter=',')
    
        all_data.append(loaded_data)

    all_data = np.concatenate(all_data)

    # Create a histogram of the combined data:      
    bin_width = np.linspace(((1 / N) + (1 /(2 * N))), 1, 101)

    counts, bins = np.histogram(all_data, bins=bin_width)

    bin_centers = (bins[:-1] + bins[1:]) / 2

    riemann_sum = np.sum(counts * (bin_centers[1] - bin_centers[0]))

    all_normalized_counts = counts / riemann_sum

    print(f"Area under simulation curve {np.sum( all_normalized_counts * (bin_centers[1] - bin_centers[0]))}")

    plt.plot(bin_centers, all_normalized_counts, marker='o' , label=f'all Data_v={v}_b={b}', color=color)

plt.legend()
plt.xlabel("Frequency")
plt.ylabel("Normalized Counts")
plt.title("Normalized Frequency Distribution")
plt.show()


#plotting analytical answer:
for i, v in enumerate(v_values):
 
    color = color_cycle[i % len(color_cycle)]
      
    B = 2 * N * 2 * v
    
    f1_values = f1(bin_centers, B)  
    
    riemann_sum_analytical = np.sum(f1_values * (bin_centers[1] - bin_centers[0]))
    
    normalized_curve = f1_values / riemann_sum_analytical
    
    print(f"Area under analytical solution curve for v={v}_b={b}:{np.sum(normalized_curve) * (bin_centers[1] - bin_centers[0])}")
    
    plt.plot(bin_centers, normalized_curve, linestyle='--', label=f'Analytical v={v}_b={b}',color=color)

plt.xlabel('Frequency')
plt.ylabel('Normalized Counts / Normalized Analytical Values')
plt.title('SFS Fluctuating Selection & Normalized Analytical Solution')
plt.legend()
plt.show()

#%%
#evaluating genetic variation for aggregated data with vectorized bias and selective fluctuation:
a = 10**4
batch_size = 10**4
num_batches = a // batch_size

output_directory = r"C:\Users\Zahra\research codes -  fluctuating selection"

GV_values = np.zeros((len(v_values), len(b_values)))

# Loop over v values:
for i, v in enumerate(v_values):
    
    # Loop over b values:
    for j, b in enumerate(b_values):
        
        all_data = []

        for batch in range(num_batches):
        
            V = np.loadtxt(f"{output_directory}\\p_b{batch}_v={v}_b={b}.txt", delimiter=',')
    
            all_data.append(V)

        all_data = np.concatenate(all_data)
 
        GV = (1 / len(all_data)) * 2 * np.sum(all_data * (1 - all_data))
       
        print(f"GV for v = {v}: {GV}")
 
        GV_values[i, j] = GV

# Plotting the heatmap:
plt.imshow(GV_values, extent=[min(b_values), max(b_values), min(v_values), max(v_values)], aspect='auto', origin='lower')
plt.colorbar(label='Genetic Variation (GV)')
plt.xlabel('b values')
plt.ylabel('v values')
plt.title('Genetic Variation')
plt.show()

#%%
# Record the end time
end_time = time.time()

# Calculate the total running time
running_time = end_time - start_time
print("Total running time:", running_time, "seconds")

#%%
#create a 3D plot for GV
from mpl_toolkits.mplot3d import Axes3D

# Create 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create a meshgrid for v_values and b_values
V, B = np.meshgrid(v_values, b_values)

# Plot the 3D surface
surface = ax.plot_surface(B, V, GV_values, cmap='viridis')

# Add color bar
fig.colorbar(surface, ax=ax, label='Genetic Variation (GV)')

# Set labels
ax.set_xlabel('b values')
ax.set_ylabel('v values')
ax.set_zlabel('Genetic Variation (GV)')
ax.set_title('Genetic Variation in 3D')

# Show the plot
plt.show()



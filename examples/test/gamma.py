import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# Parameters for the Gamma distribution
shape = 0.0025  # k (shape parameter)
scale = 40000  # theta (scale parameter)

# Generate the Gamma distribution samples
gamma_samples = np.random.gamma(shape, scale, size=10000)

# Plot the Gamma distribution
plt.hist(gamma_samples, bins=50, density=True, alpha=0.6, color='b')

# Plot the theoretical Gamma distribution
x = np.linspace(0, max(gamma_samples), 1000)
pdf = stats.gamma.pdf(x, shape, scale=scale)
plt.plot(x, pdf, 'r-', lw=2)

plt.title('Gamma Distribution (k=0.0025, θ=40000)')
plt.xlabel('Value')
plt.ylabel('Density')
plt.show()

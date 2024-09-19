import matplotlib.pyplot as plt 

# graph misc stuff for HHRF results

x = [1, 3, 5, 10, 20]
cheap_hhrf = [0.654, 0.583, 0.554, 0.522, 0.496]
expensive_hhrf = [0.562, 0.490, 0.459, 0.424, 0.398]

no_promotion_cheap_hhrf = 0.454
no_promotion_expensive_hhrf = 0.355

fig, ax = plt.subplots()
ax.plot(x, cheap_hhrf, "go-", label="Cheap query HHRF")
ax.plot(x, expensive_hhrf, "mo-", label="Expensive query HHRF")
ax.plot(x, [no_promotion_cheap_hhrf]*len(cheap_hhrf), "g--", label="Cheap query HHRF w/o promotions")
ax.plot(x, [no_promotion_expensive_hhrf]*len(cheap_hhrf), "m--", label="Expensive query HHRF w/o promotions")
ax.grid(True)
ax.set_xlabel("Promotion threshold")
ax.set_ylabel("HHRF")
ax.set_title("HHRF vs. promotion threshold value")
#ax.set_xlim((0, max(x)*1.2))
ax.legend()
plt.show()

num_promotions = [213.000, 81.000, 38.315, 12.800, 4.000]

fig, ax = plt.subplots() 
ax.plot(x, num_promotions, "ko-") 
ax.grid(True)
ax.set_xlabel("Promotion threshold")
ax.set_ylabel("Number of promotions (thousands)")
ax.set_title("Number of promotions vs. promotion threshold value")
plt.show()
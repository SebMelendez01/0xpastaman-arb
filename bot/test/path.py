import math

# DEX data 
dex1 = {"tendered": {"Token 1": 411.01352613432846}, 
        "received": {"Token 2": 582.5791440289852}}
        
dex2 = {"tendered": {"Token 2": 2267.8990523453103},
        "received": {"Token 1": 2262.7673244744074}}
        
dex3 = {"tendered": {"Token 1": 1851.7547758001347},
        "received": {"Token 2": 2141.6406491549933}}

dexes = [dex1, dex2, dex3]

# Minimum USD required to get to each dex
min_usd = [math.inf] * len(dexes)  

# Backpointers for optimal path  
backptrs = [None] * len(dexes)

# Initialize first DEX 
min_usd[0] = 0

def simulate_transfer(prev_tokens, dex):
  need_tokens = dex["tendered"]
  delta_usd = 0
  
  for token, amount in need_tokens.items():
    if prev_tokens.get(token, 0) < amount:
      purchase = amount - prev_tokens.get(token, 0)
      delta_usd += purchase * get_token_price(token)
      
  return delta_usd

def get_token_price(token):
  if token == "Token 1": return 1
  if token == "Token 2": return 1
  return 0

for i in range(1, len(dexes)):
  for j in range(i):
    # Simulate transfer from DEX j to i
    delta_usd = simulate_transfer(dexes[j]["received"], dexes[i])
    
    if min_usd[j] + delta_usd < min_usd[i]:
      min_usd[i] = min_usd[j] + delta_usd
      backptrs[i] = j
      
# Build optimal path using backpointers
opt_path = []  
i = len(dexes) - 1
while i is not None:
  opt_path.append(dexes[i])
  i = backptrs[i]
  
# Print results  
print("Optimal path:", opt_path[::-1]) 
print("Minimum USD:", min_usd[-1])
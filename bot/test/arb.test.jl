using CFMMRouter
using LinearAlgebra

# # Create three pools of the same tokens, no fees (γ=1)
ETH_USDT = ProductTwoCoin([17211.143709019695896738, 32095310.257553], .997, [1, 2])
USDC_ETH = ProductTwoCoin([29114885.392256, 15654.757443890438424937], .997, [3, 1])
DAI_USDC = ProductTwoCoin([10843872.083360015921060170, 10839678.889185], .997, [4, 3])
PEPE_ETH = ProductTwoCoin([3550980725573.515105019682341127, 2835.342137754972254531], .997, [5, 1])
# weighted_pool = GeometricMeanTwoCoin([1e4, 2e4], [.4, .6], 1, [1, 2])


# Build a routing problem with price vector = [1.0, 1.0]
prices = [1876.56, .9997, 1, .9997, .000001343] #Do you have to normalize the price vector
router = Router(
    LinearNonnegative(prices),
    [ETH_USDT, USDC_ETH, DAI_USDC, PEPE_ETH],
    5,
)


# Create three pools of the same tokens, no fees (γ=1)
# equal_pool = ProductTwoCoin([32322919.094088, 17061.904929743891441145], .997, [1, 2])
# small_pool = ProductTwoCoin([1000, 1], .997, [1, 2])
# weighted_pool = GeometricMeanTwoCoin([1e4, 2e4], [.4, .6], 1, [1, 2])

# Build a routing problem with price vector = [1.0, 1.0]
# prices = [1, 1876.56]
# router = Router(
#     LinearNonnegative(prices),
#     [equal_pool, small_pool],
#     2,
# )

# # Create three pools of the same tokens, no fees (γ=1)
# equal_pool = ProductTwoCoin([2e3, 1e3], .997, [1, 2])
# unequal_small_pool = ProductTwoCoin([1.5e8, 1e8], .997, [2, 1])
# # weighted_pool = GeometricMeanTwoCoin([1e4, 2e4], [.4, .6], 1, [1, 2])

# # Build a routing problem with price vector = [1.0, 1.0]
# prices = ones(2)
# router = Router(
#     LinearNonnegative(prices),
#     [equal_pool, unequal_small_pool],
#     2,
# )


# Optimize!
route!(router)

# Print results
Ψ = netflows(router)
println("Net trade: $Ψ")
println("Profit: \$$(dot(prices, Ψ))")


# Print individual trades 
for (i, (Δ, Λ)) in enumerate(zip(router.Δs, router.Λs))
    tokens = router.cfmms[i].Ai
    println("CFMM $i:")
    println("\tTendered basket:")
    for (ind, δ) in enumerate(Δ)
        if δ > eps()
            print("\t  $(tokens[ind]): $(δ)")
        end
    end
    println("\n\tRecieved basket:")
    for (ind, λ) in enumerate(Λ)
        if λ > eps()
            print("\t  $(tokens[ind]): $(λ)")
        end
    end
    print("\n")
end
using CFMMRouter
using LinearAlgebra
using Base
using JSON


# type = CFFM Type[("ProductTwoCoin", pool), "BoundedProduct", ...]
# pools = [[R, γ, idx], [k, α, β, R_1, R_2]]

Base.@kwdef mutable struct Token
    index::UInt64 = 0
    amount::Float64 = 0 
    price::Float64 = 0
end

Base.@kwdef mutable struct Trade
    address::String = ""
    δ::Token = Token()
    λ::Token = Token()
end


struct Calldata
    flashloan::Vector{Float64}
    trades::Vector{Trade}
end

hex(n) = string(n, base = 16)


function f(type, pools, prices)

    builtpools = []
    for i in eachindex(pools)
        if(cmp(type[i][1], "ProductTwoCoin") == 0)
            push!(builtpools, ProductTwoCoin(pools[i][1], pools[i][2], pools[i][3]))
        elseif(cmp(type[i][1], "GeometricMeanTwoCoin") == 0)
            push!(builtpools, GeometricMeanTwoCoin(pools[i][1], pools[i][2], pools[i][3], pools[i][4]))
        end
    end

    builtpools = convert(Array{CFMM{Float64}}, builtpools)
    router = Router(
        LinearNonnegative(prices),
        builtpools,
        length(prices),
    )

    # Optimize!
    route!(router)

    # Print results
    Ψ = netflows(router)
    println("\tNet trade: $Ψ")
    println("\tProfit: \$$(dot(prices, Ψ))")

    trades = Vector{Trade}()


    """
    Build a trades vector
    """
    for (i, (Δ, Λ)) in enumerate(zip(router.Δs, router.Λs))
        trade = Trade()
        tokens = router.cfmms[i].Ai
        trade.address = hex(type[i][2])

        # println("0x$(hex(type[i][2])):")
        # println("\tTendered basket:")
        
        # Only one token on each since currently each DEX only has 2 tokens
        # Multitoken DEX like balancer could have multiple tokens tendered or received
        for (ind, δ) in enumerate(Δ)
            if δ > eps()
                # print("\t  $(tokens[ind]): $(δ) --> USD \$$(prices[tokens[ind]] * (δ))")
                trade.δ.index = tokens[ind]
                trade.δ.amount = δ
                trade.δ.price = prices[tokens[ind]]
            end
        end
        # println("\n\tReciexed basket:")
        for (ind, λ) in enumerate(Λ)
            if λ > eps()
                trade.λ.index = tokens[ind]
                trade.λ.amount = λ
                trade.λ.price = prices[tokens[ind]]
                # print("\t  $(tokens[ind]): $(λ) --> USD \$$(prices[tokens[ind]] * (λ))")
            end
        end
        push!(trades, trade)
        # print("\n")
    end
    
    """
    Find the optimal trading path
    """

    """
    Find Kickstarted Tokens
    """
    kickstart = zeros(length(prices))
    current_tokens = zeros(length(prices))

    for trade in trades
        if current_tokens[trade.δ.index] >= trade.δ.amount
            current_tokens[trade.δ.index] -= trade.δ.amount
        else
            _amount = trade.δ.amount - current_tokens[trade.δ.index]
            kickstart[trade.δ.index] += _amount
        end
        current_tokens[trade.λ.index] += trade.λ.amount
    end

    println("\n--------------------TOKENS REQUIRED TO KICKSTART ARBITRAGE--------------------\n")
    println(kickstart)


    calldata = Calldata(kickstart, trades)
    # println(calldata)
    j = JSON.json(calldata)
    return j

end
defmodule Gateway.Application do
  use Application
  require Logger

  def start(_type, _args) do
    restaurant_management_services = :ets.new(:services, [:set, :public])
    food_ordering_services = :ets.new(:services, [:set, :public])

    :ets.insert(restaurant_management_services, {:service_1, "http://restaurantmanagement:9000"})
    :ets.insert(restaurant_management_services, {:service_2, "http://restaurantmanagement:9001"})
    :ets.insert(restaurant_management_services, {:service_3, "http://restaurantmanagement:9002"})
    :ets.insert(restaurant_management_services, {:service_4, "http://restaurantmanagement:9003"})

    :ets.insert(food_ordering_services, {:service_1, "http://foodordering:8000"})
    :ets.insert(food_ordering_services, {:service_2, "http://foodordering:8001"})
    :ets.insert(food_ordering_services, {:service_3, "http://foodordering:8002"})
    :ets.insert(food_ordering_services, {:service_4, "http://foodordering:8003"})

    children = [
      {Plug.Cowboy, scheme: :http, plug: Gateway.Router, options: [port: 4000]},
      {Redix, {"redis://localhost:6379", [name: :redix]}},
      %{
        id: :restaurant_management,
        start: {LoadBalancer, :start_link, [{:ets.tab2list(restaurant_management_services), :restaurant_management}]}
      },
      %{
        id: :food_ordering,
        start: {LoadBalancer, :start_link, [{:ets.tab2list(food_ordering_services), :food_ordering}]}
      },
      Gateway.PromEx
    ]

    Logger.info("Visit: http://localhost:4000")
    opts = [strategy: :one_for_one, name: App.Supervisor]
    Supervisor.start_link(children, opts)
  end
end

defmodule Gateway.Coordinator do
  use GenServer
  require Logger

  def start_link(name) do
    GenServer.start_link(__MODULE__, name, name: name)
  end

  def init(_) do
    {:ok, %{food_ordering: 0, restaurant_management: 0}}
  end

  def handle_call(:first_check, _from, state) do
    updated_state =
      case make_request("http://foodordering-1:8000") do
        {:ok, %{status_code: 200}} ->
          Logger.info("Connection check to food_ordering DB - [GOOD]")
          Map.put(state, :food_ordering, 1)
        _ ->
          Logger.info("Connection check to food_ordering DB - [BAD]")
          Map.put(state, :food_ordering, 0)
      end

    {:reply, nil, updated_state}
  end

  def handle_call(:second_check, _from, state) do
    updated_state =
      case make_request("http://restaurantmanagement-1:9000") do
        {:ok, %{status_code: 200}} ->
          Logger.info("Connection check to restaurant_management DB - [GOOD]")
          Map.put(state, :restaurant_management, 1)
        _ ->
          Logger.info("Connection check to restaurant_management DB - [BAD]")
          Map.put(state, :restaurant_management, 0)
      end

    {:reply, nil, updated_state}
  end

  def handle_call(:get_state, _from, state) do
    {:reply, state, state}
  end

  defp make_request(service) do
    case HTTPoison.get!("#{service}/health") do
      %{status_code: code} -> {:ok, %{status_code: code}}
      _ -> {:error, "Failed to make the request"}
    end
  rescue
    _ -> {:error, "Failed to make the request"}
  end
end

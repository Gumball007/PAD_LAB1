defmodule Gateway.Router do
  use Plug.Router
  require Logger

  plug Plug.Parsers,
       parsers: [:json],
       pass:  ["application/json"],
       json_decoder: Jason

  plug :match
  plug :dispatch

  defp food_ordering_host() do
    "http://foodordering:8000"
  end

  defp restaurant_management_host() do
    "http://restaurantmanagement:9000"
  end

  post "/orders" do
    {:ok, r} = HTTPoison.post("#{food_ordering_host()}/orders", Jason.encode!(conn.body_params), %{"Content-Type" => "application/json"})

    conn
    |> put_resp_content_type("application/json")
    |> send_resp(r.status_code, r.body)
  end

  get "/orders/:order_id" do
    case Redix.command(:redix, ["GET", "order/#{order_id}"]) do

      {:ok, nil} ->
        {:ok, r} = HTTPoison.get("#{food_ordering_host()}/orders/#{order_id}", %{"Content-Type" => "application/json"})
        Redix.command!(:redix, ["SETEX", "order/#{order_id}", 3600, r.body])

        conn
        |> put_resp_content_type("application/json")
        |> send_resp(r.status_code, r.body)

      {:ok, cached_order} ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(200, cached_order)
    end
  end

  get "/orders/:order_id/items" do

    case Redix.command(:redix, ["GET", "order:items/#{order_id}"]) do

      {:ok, nil} ->
        {:ok, r} = HTTPoison.get("#{food_ordering_host()}/orders/#{order_id}/items", %{"Content-Type" => "application/json"})
        Redix.command!(:redix, ["SETEX", "order:items/#{order_id}", 3600, r.body])

        conn
        |> put_resp_content_type("application/json")
        |> send_resp(r.status_code, r.body)

      {:ok, cached_order_items} ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(200, cached_order_items)
    end
  end


  get "/restaurants" do

    case Redix.command(:redix, ["GET", "restaurants"]) do

      {:ok, nil} ->
        {:ok, r} = HTTPoison.get("#{restaurant_management_host()}/restaurants", %{"Content-Type" => "application/json"})
        Redix.command!(:redix, ["SETEX", "restaurants", 3600, r.body])

        conn
        |> put_resp_content_type("application/json")
        |> send_resp(r.status_code, r.body)

      {:ok, cached_restaurants} ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(200, cached_restaurants)
    end
  end

  get "/restaurants/:restaurant_id" do

    case Redix.command(:redix, ["GET", "restaurant/#{restaurant_id}"]) do

      {:ok, nil} ->
        {:ok, r} = HTTPoison.get("#{restaurant_management_host()}/restaurants/#{restaurant_id}", %{"Content-Type" => "application/json"})
        Redix.command!(:redix, ["SETEX", "restaurant/#{restaurant_id}", 3600, r.body])

        conn
        |> put_resp_content_type("application/json")
        |> send_resp(r.status_code, r.body)

      {:ok, cached_restaurant} ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(200, cached_restaurant)
    end
end

  get "/status" do
    {:ok, r} = Jason.encode(%{"Gateway": "healthy"})
    Redix.command(:redix, ["SET", "mykey", "foo"])
    {:ok, test} = Redix.command(:redix, ["GET", "mykey"])
    IO.inspect test

    send_resp(put_resp_content_type(conn, "application/json"), 200, r)
  end

  match _ do
    {:ok, r} = Jason.encode(%{"Detail": "Method not allowed"})
    send_resp(put_resp_content_type(conn, "application/json"), 200, r)
  end
end

defmodule Gateway.Router do
  use Plug.Router

  plug Plug.Parsers,
       parsers: [:json],
       pass:  ["application/json"],
       json_decoder: Jason

  plug :match
  plug :dispatch

  defp food_ordering_host() do
    "http://localhost:8000"
  end

  defp restaurant_management_host() do
    "http://localhost:9000"
  end

  post "/orders" do
    {:ok, r} = HTTPoison.post("#{food_ordering_host()}/orders", Jason.encode!(conn.body_params), %{"Content-Type" => "application/json"})

    conn
    |> put_resp_content_type("application/json")
    |> send_resp(200, r.body)
  end

  get "/orders/:order_id" do
    {:ok, r} = HTTPoison.get("#{food_ordering_host()}/orders/#{order_id}", %{"Content-Type" => "application/json"})

    conn
    |> put_resp_content_type("application/json")
    |> send_resp(200, r.body)
  end

  get "/restaurants" do
    {:ok, r} = HTTPoison.get("#{restaurant_management_host()}/restaurants", %{"Content-Type" => "application/json"})

    conn
    |> put_resp_content_type("application/json")
    |> send_resp(200, r.body)
  end

  get "/restaurants/:restaurant_id" do
    {:ok, r} = HTTPoison.get("#{restaurant_management_host()}/restaurants/#{restaurant_id}", %{"Content-Type" => "application/json"})

    conn
    |> put_resp_content_type("application/json")
    |> send_resp(200, r.body)
  end

  get "/status" do
    {:ok, r} = Jason.encode(%{"Gateway": "healthy"})
    send_resp(put_resp_content_type(conn, "application/json"), 200, r)
  end

  match _ do
    {:ok, r} = Jason.encode(%{"Detail": "Method not allowed"})
    send_resp(put_resp_content_type(conn, "application/json"), 200, r)
  end
end

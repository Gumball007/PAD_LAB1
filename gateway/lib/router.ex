defmodule Gateway.Router do
  use Plug.Router
  require Logger

  plug Plug.Parsers,
       parsers: [:json],
       pass:  ["application/json"],
       json_decoder: Jason

  plug :match
  plug :dispatch

  defp post_with_retry(endpoint, service, body_params, retries) do
    case post_with_retry_impl(endpoint, service, body_params, retries) do
      {:ok, response} -> {:ok, response}
      :reroutes_exceded -> {:reroutes_exceded, %HTTPoison.Error{}}
    end
  end

  defp post_with_retry_impl(_endpoint, _service, _body_params, 0), do: :reroutes_exceded

  defp post_with_retry_impl(endpoint, service, body_params, retries) do
    {_, service_host} = GenServer.call(service, :get_instance)

    case HTTPoison.post("#{service_host}/#{endpoint}", Jason.encode!(body_params), %{"Content-Type" => "application/json"}) do
      {:ok, response} ->
        {:ok, response}
      {:error, _reason} ->
        Logger.error("Reroute in service #{Atom.to_string(service)}")
        post_with_retry_impl(endpoint, service, body_params, retries - 1)
    end
  end

  defp get_with_retry(endpoint, service, retries) do
    case get_with_retry_impl(endpoint, service, retries) do
      {:ok, response} -> {:ok, response}
      :reroutes_exceded -> {:reroutes_exceded, %HTTPoison.Error{}}
    end
  end

  defp get_with_retry_impl(_endpoint, _service, 0), do: :reroutes_exceded

  defp get_with_retry_impl(endpoint, service, retries) do
    {_, service_host} = GenServer.call(service, :get_instance)

    case HTTPoison.get("#{service_host}/#{endpoint}", %{"Content-Type" => "application/json"}) do
      {:ok, response} ->
        {:ok, response}
      {:error, _reason} ->
        Logger.error("Reroute in service #{Atom.to_string(service)}")
        get_with_retry_impl(endpoint, service, retries - 1)
    end
  end

  post "/orders" do
    case post_with_retry("orders", :food_ordering, conn.body_params, 3) do
      {:ok, r} ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(r.status_code, r.body)

      {:reroutes_exceded, a} ->
        Logger.error("Number of reroutes exceded")
        {:reroutes_exceded, a}
        send_resp(conn, 500, "Something is bad with server")
    end
  end

  get "/orders/:order_id" do
    case Redix.command(:redix, ["GET", "order/#{order_id}"]) do

      {:ok, nil} ->

        case get_with_retry("orders/#{order_id}", :food_ordering, 3) do
          {:ok, r} ->
            Redix.command!(:redix, ["SETEX", "order/#{order_id}", 3600, r.body])

            conn
            |> put_resp_content_type("application/json")
            |> send_resp(r.status_code, r.body)

          {:reroutes_exceded, a} ->
            Logger.error("Number of reroutes exceded")
            {:reroutes_exceded, a}
            send_resp(conn, 500, "Something is bad with server")

        end

      {:ok, cached_order} ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(200, cached_order)
    end
  end

  get "/orders/:order_id/items" do

    case Redix.command(:redix, ["GET", "order:items/#{order_id}"]) do

      {:ok, nil} ->
        case get_with_retry("orders/#{order_id}/items", :food_ordering, 3) do
          {:ok, r} ->
            Redix.command!(:redix, ["SETEX", "order/#{order_id}/items", 3600, r.body])

            conn
            |> put_resp_content_type("application/json")
            |> send_resp(r.status_code, r.body)

          {:reroutes_exceded, a} ->
            Logger.error("Number of reroutes exceded")
            {:reroutes_exceded, a}
            send_resp(conn, 500, "Something is bad with server")
        end

      {:ok, cached_order_items} ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(200, cached_order_items)
    end
  end


  get "/restaurants" do

    case Redix.command(:redix, ["GET", "restaurants"]) do

      {:ok, nil} ->
        case get_with_retry("restaurants", :restaurant_management, 3) do
          {:ok, r} ->
            Redix.command!(:redix, ["SETEX", "restaurants", 3600, r.body])

            conn
            |> put_resp_content_type("application/json")
            |> send_resp(r.status_code, r.body)

          {:reroutes_exceded, a} ->
            Logger.error("Number of reroutes exceded")
            {:reroutes_exceded, a}
            send_resp(conn, 500, "Something is bad with server")
        end

      {:ok, cached_restaurants} ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(200, cached_restaurants)
    end
  end

  get "/restaurants/:restaurant_id" do

    case Redix.command(:redix, ["GET", "restaurant/#{restaurant_id}"]) do

      {:ok, nil} ->
        case get_with_retry("restaurants/#{restaurant_id}", :restaurant_management, 3) do
          {:ok, r} ->
            Redix.command!(:redix, ["SETEX", "restaurant/#{restaurant_id}", 3600, r.body])

            conn
            |> put_resp_content_type("application/json")
            |> send_resp(r.status_code, r.body)

          {:reroutes_exceded, a} ->
            Logger.error("Number of reroutes exceded")
            {:reroutes_exceded, a}
            send_resp(conn, 500, "Something is bad with server")
        end


      {:ok, cached_restaurant} ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(200, cached_restaurant)
    end
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

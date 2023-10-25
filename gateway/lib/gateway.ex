defmodule Gateway.Application do
  use Application
  require Logger

  def start(_type, _args) do
    children = [
      {Plug.Cowboy, scheme: :http, plug: Gateway.Router, options: [port: 4000]},
      {Redix, {"redis://redis:6379", [name: :redix]}}
    ]

    Logger.info("Visit: http://localhost:4000")
    opts = [strategy: :one_for_one, name: App.Supervisor]
    Supervisor.start_link(children, opts)
  end
end

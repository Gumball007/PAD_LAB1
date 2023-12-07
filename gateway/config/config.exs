import Config

config :gateway, Gateway.PromEx,
  disabled: false,
  manual_metrics_start_delay: :no_delay,
  drop_metrics_groups: [],
  grafana: [
    host: "http://grafana1:3000",
    # Authenticate via Basic Auth
    username: "admin",
    password: "admin",
    upload_dashboards_on_start: true
  ],
  metrics_server: :disabled

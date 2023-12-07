defmodule LoadBalancer do
  use GenServer

  def start_link({list, name}) do
    GenServer.start_link(__MODULE__, list, name: name)
  end

  def init(list) do
    {:ok, %{list: list, index: 0}}
  end

  def handle_call(:get_instance, _from, %{list: list, index: index} = state) do
    item = Enum.at(list, index)
    next_index = rem((index + 1), length(list))
    {:reply, item, %{state | index: next_index}}
  end
end

# Use an official Elixir runtime as a parent image
FROM elixir:slim

# Set the working directory inside the container
WORKDIR /app

# Copy the mix.exs and mix.lock files to the container
COPY mix.exs mix.lock ./

# Install Hex and rebar
RUN mix local.hex --force && mix local.rebar --force

# Install project dependencies
RUN mix deps.get

# Copy the rest of the application code
COPY . .

# Set the environment variable for a production release
ENV MIX_ENV=prod

# Compile the Elixir application
RUN mix compile

# Expose any necessary ports (replace 4000 with your application's port)
EXPOSE 4000

# Command to start your Elixir application (modify this to match your app's entry point)
CMD ["mix", "run", "--no-halt"]

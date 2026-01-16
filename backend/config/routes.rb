Rails.application.routes.draw do
  root "home#index"
  get "home/login"
  get "field/index"

  # Health check
  get "up" => "rails/health#show", as: :rails_health_check
end
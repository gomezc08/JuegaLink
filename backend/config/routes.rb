Rails.application.routes.draw do
  resources :users#, path: "members"
  root "home#index"
  get "home/login"
  get "home/signup"

  # Health check
  get "up" => "rails/health#show", as: :rails_health_check
end
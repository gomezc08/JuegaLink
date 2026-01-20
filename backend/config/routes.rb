Rails.application.routes.draw do
  devise_for :users
  post "fyp/login", to: "fyp#login"
  get "fyp/index"
  get "fyp/profile"
  get "fyp/search"
  root "home#index"
  get "home/login"
  post "home/login", to: "home#login_post"
  get "home/signup"
  post "home/signup", to: "home#signup_post"
  delete "home/logout", to: "home#logout", as: :home_logout

  # Health check
  get "up" => "rails/health#show", as: :rails_health_check
end
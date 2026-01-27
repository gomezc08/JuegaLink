Rails.application.routes.draw do
  devise_for :users
  post "fyp/login", to: "fyp#login"
  get "fyp/index"
  get "fyp/profile"
  get "fyp/edit_profile"
  patch "fyp/profile", to: "fyp#update_profile"
  put "fyp/profile", to: "fyp#update_profile"
  get "fyp/search"
  root "home#index"
  get "fyp/user_page/:username", to: "fyp#user_page", as: :fyp_user_page
  post "fyp/follow", to: "fyp#follow", as: :fyp_follow
  post "fyp/unfollow", to: "fyp#unfollow", as: :fyp_unfollow
  get "fyp/friends", to: "fyp#friends", as: :fyp_friends
  get "fyp/notifications", to: "fyp#notifications", as: :fyp_notifications
  get "home/login"
  post "home/login", to: "home#login_post"
  get "home/signup"
  post "home/signup", to: "home#signup_post"
  delete "home/logout", to: "home#logout", as: :home_logout

  # Health check
  get "up" => "rails/health#show", as: :rails_health_check
end
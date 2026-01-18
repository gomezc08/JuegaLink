json.extract! user, :id, :user_name, :age, :city, :state, :bio, :created_at, :updated_at
json.url user_url(user, format: :json)

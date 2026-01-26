require 'net/http'
require 'json'
require 'uri'

class MlApiService
  BASE_URL = ENV.fetch('ML_SERVICE_URL', 'http://localhost:5000')

  class << self
    def signup(username:, email:, password:)
      uri = URI("#{BASE_URL}/users/signup")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        username: username,
        email: email,
        password: password
      }.to_json

      response = http.request(request)
      handle_response(response)
    end

    def login(username:, password:)
      uri = URI("#{BASE_URL}/users/login")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        username: username,
        password: password
      }.to_json

      response = http.request(request)
      handle_response(response)
    end

    def update_user(username:, **params)
      uri = URI("#{BASE_URL}/users/update")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Put.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        username: username,
        **params
      }.to_json

      response = http.request(request)
      handle_response(response)
    end

    def get_friends(username:)
      uri = URI("#{BASE_URL}/users/#{username}/friends")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path, 'Content-Type' => 'application/json')

      response = http.request(request)
      handle_response(response)
    end

    def get_user(username:)
      uri = URI("#{BASE_URL}/users/#{username}")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path, 'Content-Type' => 'application/json')
      response = http.request(request)
      handle_response(response)
    end

    def search_users(query:)
      uri = URI("#{BASE_URL}/search/users")
      uri.query = URI.encode_www_form(q: query)
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path + '?' + uri.query, 'Content-Type' => 'application/json')

      response = http.request(request)
      handle_response(response)
    end

    def search_fields(query:)
      uri = URI("#{BASE_URL}/search/fields")
      uri.query = URI.encode_www_form(q: query)
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path + '?' + uri.query, 'Content-Type' => 'application/json')

      response = http.request(request)
      handle_response(response)
    end

    private

    def handle_response(response)
      case response.code.to_i
      when 200..299
        JSON.parse(response.body)
      when 401
        error_data = JSON.parse(response.body) rescue { error: 'Invalid credentials' }
        { error: error_data['error'] || 'Invalid credentials', success: false }
      when 400..499
        error_data = JSON.parse(response.body) rescue { error: 'Client error' }
        { error: error_data['error'] || 'Client error', success: false }
      when 500..599
        error_data = JSON.parse(response.body) rescue { error: 'Server error' }
        { error: error_data['error'] || 'Server error', success: false }
      else
        { error: "Unexpected response: #{response.code}", success: false }
      end
    end
  end
end

require "test_helper"

class FieldControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get field_index_url
    assert_response :success
  end
end

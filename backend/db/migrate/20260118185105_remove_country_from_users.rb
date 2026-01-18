class RemoveCountryFromUsers < ActiveRecord::Migration[8.1]
  def change
    remove_column :users, :country, :string
  end
end

class CreateUsers < ActiveRecord::Migration[8.1]
  def change
    create_table :users do |t|
      t.string :user_name
      t.integer :age
      t.string :city
      t.string :state
      t.string :bio

      t.timestamps
    end
  end
end

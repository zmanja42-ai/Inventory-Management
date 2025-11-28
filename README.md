# Inventory Management System

The Inventory Management System is a powerful tool designed to simplify the management of inventory across multiple factories or areas within a company. This application allows users to easily adjust inventory, log details of adjustments including who made the change and why, and facilitates easy reordering for each factory or area.



## Features

- **Manage Areas:** Create, rename, and remove areas or factories for which inventory is managed.
- **Add/Edit Parts:** Add new parts to the inventory or edit existing parts with details such as Company PN, Manufacturer PN, description, quantity, min, max, and notes.
- **Remove Parts:** Remove parts from the inventory when they are no longer needed.
- **Adjust Inventory:** Easily adjust the quantity of inventory items and keep logs of who adjusted what and why.
- **Import/Export CSV:** Import inventory data from CSV files and export the current inventory to CSV files for reporting and backup purposes.
- **Search & Filter:** Search and filter parts in the inventory for quick access.
- **Activity Log:** Maintain detailed logs of all inventory adjustments, including the user who made the adjustment and any notes explaining the reason for the changes.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/inventory-management.git
    cd inventory-management
    ```

2. Install required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:

    ```bash
    python src/main.py
    ```

## Usage

- **Manage Areas:** Click on `Manage Areas` to create, rename, or remove areas. Select an area from the dropdown to view and manage inventory for that specific area.
- **Add Part:** Click on the `Add Part` button to add a new part to the inventory. Fill in the required details and click 'Save.'
- **Edit Part:** Select a part from the list and click on the `Edit Part` button to modify its details.
- **Remove Part:** Select a part from the list and click on the `Remove Part` button to delete it from the inventory.
- **Adjust Inventory:** After selecting a part, update its quantity and log who made the adjustment and why.
- **Import CSV:** Click on `Import CSV` to upload inventory data from a CSV file.
- **Export CSV:** Click on `Export CSV` to download the current inventory data as a CSV file.
- **Search & Filter:** Use the search bar and filter dropdown to quickly find parts based on specific criteria.
- **Activity Logs:** Review the logs to see who adjusted the inventory, when it was adjusted, and any notes explaining the reason for the adjustments.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! Please fork this repository and submit pull requests.

## Contact

For questions or comments, please open an issue or reach out to the maintainer at `Zmanja42@Gmail.com`.

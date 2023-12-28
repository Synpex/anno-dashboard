// JavaScript to buildings table
    import DataTable from 'datatables.net-dt';

    let buildings_table = new DataTable('#buildings-table', {
        responsive: true,
        ordering: true,

        // config options...
    });
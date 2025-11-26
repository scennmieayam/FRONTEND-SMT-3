$(document).ready(function () {
    let editIndex = null;

    function loadData() {
        let data = JSON.parse(localStorage.getItem("users")) || [];
        $("#tableData").empty();
        data.forEach((item, index) => {
            $("#tableData").append(`
                <tr>
                    <td>${item.nama}</td>
                    <td>${item.alamat}</td>
                    <td>
                        <button class="action-btn edit-btn" data-index="${index}">Edit</button>
                        <button class="action-btn delete-btn" data-index="${index}">Delete</button>
                    </td>
                </tr>
            `);
        });
    }

    function saveData(data) {
        localStorage.setItem("users", JSON.stringify(data));
    }

    $("#addBtn").click(function () {
        let nama = $("#nama").val().trim();
        let alamat = $("#alamat").val().trim();
        if (nama === "" || alamat === "") {
            alert("Nama dan Alamat tidak boleh kosong!");
            return;
        }
        let data = JSON.parse(localStorage.getItem("users")) || [];
        data.push({ nama, alamat });
        saveData(data);
        $("#nama").val("");
        $("#alamat").val("");
        loadData();
    });

    $("#tableData").on("click", ".delete-btn", function () {
        let index = $(this).data("index");
        let data = JSON.parse(localStorage.getItem("users")) || [];
        data.splice(index, 1);
        saveData(data);
        loadData();
    });

    $("#tableData").on("click", ".edit-btn", function () {
        editIndex = $(this).data("index");
        let data = JSON.parse(localStorage.getItem("users")) || [];
        let user = data[editIndex];
        $("#nama").val(user.nama);
        $("#alamat").val(user.alamat);
        $("#addBtn").hide();
        $("#updateBtn").show();
    });

    $("#updateBtn").click(function () {
        let nama = $("#nama").val().trim();
        let alamat = $("#alamat").val().trim();
        let data = JSON.parse(localStorage.getItem("users")) || [];
        data[editIndex] = { nama, alamat };
        saveData(data);
        $("#nama").val("");
        $("#alamat").val("");
        $("#addBtn").show();
        $("#updateBtn").hide();
        loadData();
    });

    loadData();
});
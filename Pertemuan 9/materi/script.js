$(document).ready(function () {
    $("#addBtn").click(function () {
        let taskText = $("#taskinput").val().trim();
        if (taskText === "") {
            alert("Tugas tidak boleh kosong!");
            return;
        }
        let li = $("<li></li>").text(taskText);
        let deleteBtn = $("<button class='delete-btn'>Hapus</button>");
        li.append(deleteBtn);
        $("#tasklist").append(li);
        $("#taskinput").val("");
    });

    $("#tasklist").on("click", "li", function () {
        $(this).toggleClass("task-done");
    });

    $("#tasklist").on("click", ".delete-btn", function (event) {
        event.stopPropagation();
        $(this).parent().fadeOut(300, function () {
            $(this).remove();
        });
    });
});
<div class="a">
    <div class="b">
        <div class="link-box">
            <a class="text" href="/profile">Profile</a>
        </div>
        <div class="link-box">
            <a class="text" href="/profile">Profile2</a>
    </div>
    </div>
</div>

<style>
    .a {
        position: absolute;
        top: 0;
        right: 0;
        background-color: black;
        width: 100%;
        height: 30px;
    }
    .b {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }
    .text {
        color: white;
    }
    .link-box:hover {
        background-color: blue;
        text-align: center;
    }
    a:hover {
        text-decoration: none;
    }
</style>
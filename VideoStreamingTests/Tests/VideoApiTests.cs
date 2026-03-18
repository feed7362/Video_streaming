using System.Net;
using Dapper;
using FluentAssertions;
using Microsoft.Data.SqlClient;
using RestSharp;
using Serilog;
using NUnit.Framework;

namespace VideoStreamingTests.Tests;

[TestFixture]
public class VideoApiTests
{
    private RestClient _client;
    private ILogger _logger;
    private readonly string _connectionString = "Server=localhost;Database=VideoDb;User Id=sa;Password=your_password;";

    [SetUp]
    public void Setup()
    {
        _client = new RestClient("http://localhost:8080");

        _logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .WriteTo.Console(outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
            .WriteTo.File("logs/api_tests_.log", rollingInterval: RollingInterval.Day)
            .CreateLogger();

        _logger.Information("--- Підготовка до тесту (SetUp) ---");
    }

    [Test]
    public async Task FullVideoLifecycle_Test()
    {
        _logger.Information("Запуск E2E сценарію");

        var uploadRequest = new RestRequest("/api/video/upload", Method.Post);
        uploadRequest.AddJsonBody(new { Title = "NUnit E2E Video", Description = "Testing with NUnit" });

        var uploadResponse = await _client.ExecuteAsync<Video>(uploadRequest);
        uploadResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var videoId = uploadResponse.Data!.Id;
        _logger.Debug("Відео створено. ID: {VideoId}", videoId);

        var getRequest = new RestRequest($"/api/video/info/{videoId}");
        var getResponse = await _client.ExecuteAsync<Video>(getRequest);

        getResponse.StatusCode.Should().Be(HttpStatusCode.OK);
        getResponse.Data!.Title.Should().Be("NUnit E2E Video");

        var deleteRequest = new RestRequest($"/api/files/delete_video/{videoId}", Method.Delete);
        var deleteResponse = await _client.ExecuteAsync(deleteRequest);

        deleteResponse.StatusCode.Should().Be(HttpStatusCode.OK);
        _logger.Information("Відео {VideoId} видалено успішно", videoId);
    }

    [Test]
    public async Task GetVideo_UsingIdFromDatabase_ReturnSuccess()
    {
        _logger.Information("Отримання даних через SQL (Dapper)...");

        using var connection = new SqlConnection(_connectionString);
        var videoFromDb = await connection.QueryFirstOrDefaultAsync<Video>(
            "SELECT TOP 1 Id, Title FROM Videos ORDER BY NEWID()");

        videoFromDb.Should().NotBeNull("База даних не має записів");

        var request = new RestRequest($"/api/video/info/{videoFromDb.Id}");
        var response = await _client.ExecuteAsync<Video>(request);

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        response.Data!.Id.Should().Be(videoFromDb.Id);
        _logger.Information("API підтвердило дані для ID {Id}", videoFromDb.Id);
    }

    [Test]
    public async Task DeleteVideo_NonExistingId_ReturnNotFound()
    {
        var invalidId = 888888;
        _logger.Warning("Негативний тест: ID {Id}", invalidId);

        var request = new RestRequest($"/api/files/delete_video/{invalidId}", Method.Delete);
        var response = await _client.ExecuteAsync(request);

        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [TearDown]
    public void Cleanup()
    {
        _logger.Information("--- Завершення тесту та очищення (TearDown) ---");
    }
}

public class Video
{
    public int Id { get; set; }
    public string Title { get; set; }
}
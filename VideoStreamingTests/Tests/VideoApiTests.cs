using RestSharp;
using FluentAssertions;
using System.Net;
using Xunit;

namespace VideoStreamingTests.Tests;

public class VideoApiTests
{
    private readonly RestClient _client;



    //вролді ж є basurl чому тут це повторюється?
    public VideoApiTests()
    {
        _client = new RestClient("http://localhost:8080");
    }

    [Fact]
    public void GetVideo_ExistingId_ReturnSuccess()
    {
        var request = new RestRequest("/api/video/info/1", Method.Get);

        var response = _client.Execute(request);

        response.Should().NotBeNull();
    }

    //[Fact]
    //public void DeleteVideo_ExistingId_ReturnSuccess()
    //{
    //    var request = new RestRequest("/api/files/delete_video/1", Method.Delete);

    //    var response = _client.execute(request);

    //    response.StatusCode.Should().Be(HttpStatusCode.OK);
    //}

    [Fact]
    public async Task DeleteVideo_ExistingId_ReturnSuccess()
    {
        var request = new RestRequest("/api/files/delete_video/1", Method.Delete);

        try
        {
            response = await _client.ExecuteAsync(request);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }

        response.StatusCode.Should().Be{
            HttpStatusCode.OK);
        }
    }

        [Fact]
    public void UploadVideo_ValidData_returnSuccess()
    {
        var request = new RestRequest("/api/video/upload", Method.Post);

        var response = _client.Execute(request);

        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public void DownloadVideo_ExistingId_ReturnSuccess()
    {
        var request = new RestRequest("/api/files/download_video/123", Method.Get);

        var response = _client.Execute(request);

        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public void GetVideo_CheckDetails_ReturnSuccess()
    {
        var videoId = 1;
        var request = new RestRequest($"/api/video/info/{videoId}", Method.Get);

        var response = await _client.ExecuteAsync<Video>(request);

        response.StatusCode.Should().Be(HttpStatusCode.OK);

        response.Data.Id.Should().Be(videoId);
        response.Data.Title.Should().NotBeNullOrEmpty;
    }



 
}
import {render, screen} from "@testing-library/react";
import Home from "../src/pages/Home";
import {vi, describe, it, expect} from "vitest";
import "@testing-library/jest-dom";

vi.mock("@/components/VideoPlayer", () => {
    return {
        default: ({src}: { src: string }) => (
            <div data-testid="video-player">Video source: {src}</div>
        ),
    };
});

describe("Home component", () => {
    it("renders heading and VideoPlayer", () => {
        render(<Home/>);

        expect(
            screen.getByRole("heading", {name: /My VOD MVP/i})
        ).toBeInTheDocument();

        expect(screen.getByTestId("video-player")).toHaveTextContent(
            "http://localhost:8000/videos/123/playlist.m3u8"
        );
    });
});

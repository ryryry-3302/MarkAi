"""
Command-line interface for generating and loading sample data.
"""
import argparse
import os
import logging
from sample_data.generator import generate_sample_data
from sample_data.processor import load_sample_data, process_sample_videos
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='Marketing Analytics Sample Data CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Generate sample data command
    generate_parser = subparsers.add_parser('generate', help='Generate sample data')
    generate_parser.add_argument('--output-dir', type=str, default='./data', 
                                help='Directory to output sample data files')
    generate_parser.add_argument('--days', type=int, default=30,
                                help='Number of days of data to generate')
    
    # Load sample data command
    load_parser = subparsers.add_parser('load', help='Load sample data into database')
    load_parser.add_argument('--data-dir', type=str, default='./data',
                            help='Directory containing sample data files')
    
    # Process videos command
    process_parser = subparsers.add_parser('process-videos', help='Process sample videos')
    process_parser.add_argument('--sample-dir', type=str, default='./sample_videos',
                                help='Directory containing sample videos')
    process_parser.add_argument('--temp-dir', type=str, default='./temp',
                                help='Directory to store temporary files')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == 'generate':
        logger.info(f"Generating sample data in {args.output_dir} for {args.days} days")
        generate_sample_data(args.output_dir, args.days)
    
    elif args.command == 'load':
        logger.info(f"Loading sample data from {args.data_dir}")
        # Load sample data directly using the Supabase client
        load_sample_data(args.data_dir)
    
    elif args.command == 'process-videos':
        logger.info(f"Processing sample videos from {args.sample_dir}")
        os.makedirs(args.temp_dir, exist_ok=True)
        video_data = process_sample_videos(args.sample_dir, args.temp_dir)
        logger.info(f"Processed {len(video_data)} videos")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
